from functools import lru_cache

import docker
from docker.errors import DockerException

from ..settings import get_settings

__all__ = [
    'docker_client',
    'NotAuthorizedContainer',
    'ContainerAllReadyRunning',
    'ContainerNotFound',
    'ImageNotFound',
    "DockerException"
]


class NotAuthorizedContainer(Exception):
    pass


class ContainerAllReadyRunning(Exception):
    pass


class ContainerNotFound(Exception):
    pass


class ImageNotFound(Exception):
    pass


class DockerServicesManager:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.containers = {}

    def stop_container(self, service_name: str):
        container = self.containers.pop(service_name, None)
        if container is None:
            raise ContainerNotFound(f'container for service "{service_name}" not found.')
        container.stop()
        container.remove()

    def pause(self, service_name: str):
        container = self.containers.pop(service_name, None)
        if container is None:
            raise ContainerNotFound(f'container for service "{service_name}" not found.')
        container.pause()

    def unpause(self, service_name: str):
        container = self.containers.pop(service_name, None)
        if container is None:
            raise ContainerNotFound(f'container for service "{service_name}" not found.')
        container.unpause()

    @staticmethod
    def allowed_docker_image(image_name: str):
        """
        Check if the docker image is from box's github account
        :param image_name: the name of the image e.g "ConnectAPI/some_image_name"
        :return: bool
        """
        return True
        # return image_name.startswith('boxs/')

    def pull_image(self, image_name: str):
        """Pull the image from docker hub
        """
        image = self.docker_client.images.get(image_name)
        if image:
            return image
        try:
            return self.docker_client.images.pull(image_name, tag='latest')
        except Exception:
            return None

    def run_container(self, image_name: str, environment: dict, service_name: str, bind_port: int):
        if service_name in self.containers:
            raise ContainerAllReadyRunning(f'Container {service_name} is all ready running.')
        if not self.allowed_docker_image(image_name):
            raise NotAuthorizedContainer(f'{image_name} is not from ConnectAPI docker hub account.')
        image = self.pull_image(image_name)
        if image is None:
            raise ImageNotFound(f'Image {image_name} not found on local memory and docker hub.')
        container = self.docker_client.containers.run(
            image.short_id,
            name=service_name,
            detach=True,
            network=get_settings().docker_network_name,
            hostname=service_name,
            environment=environment,
            ports={"80": bind_port},
        )
        self.containers[service_name] = container
        return container

    def stop_all(self):
        for service_name, container in self.containers.items():
            container.stop()
        self.docker_client.containers.prune()


@lru_cache
def docker_client() -> DockerServicesManager:
    return DockerServicesManager()
