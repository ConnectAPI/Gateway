from functools import lru_cache

import docker
from docker.errors import DockerException, APIError

from core.settings import get_settings

__all__ = [
    'docker_client',
    'NotAuthorizedContainer',
    'ContainerAllReadyRunning',
    'ContainerNotFound',
    'ImageNotFound',
    "DockerException"
]


DOCKERHUB_ACCOUNT = "connectapihub"


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

    def stop_container(self, short_id: str):
        container = self.containers.pop(short_id, None)
        if container is None:
            raise ContainerNotFound(f'container "{short_id}" not found.')
        container.stop()
        container.remove()

    def pause(self, short_id: str):
        container = self.containers.pop(short_id, None)
        if container is None:
            raise ContainerNotFound(f'container "{short_id}" not found.')
        container.pause()

    def unpause(self, short_id: str):
        container = self.containers.pop(short_id, None)
        if container is None:
            raise ContainerNotFound(f'container "{short_id}" not found.')
        container.unpause()

    @staticmethod
    def allowed_docker_image(image_name: str):
        """
        Check if the docker image is from box's github account
        :param image_name: the name of the image e.g "ConnectAPI/some_image_name"
        :return: bool
        """
        return image_name.startswith(f'{DOCKERHUB_ACCOUNT}/')

    def pull_image(self, image_name: str):
        """Pull the image from docker hub or just use the local image if exist"""
        image = self.docker_client.images.get(image_name)
        if image:
            return image
        try:
            return self.docker_client.images.pull(image_name, tag='latest')
        except APIError:
            return None

    def run_container(self, image_name: str, environment: dict, service_name: str):
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
        )
        self.containers[container.short_id] = container
        return container.short_id

    def stop_all(self):
        for service_name, container in self.containers.items():
            container.stop()
        self.docker_client.containers.prune()


@lru_cache
def docker_client() -> DockerServicesManager:
    return DockerServicesManager()
