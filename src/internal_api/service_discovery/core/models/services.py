from typing import Dict, Optional
from functools import lru_cache

from .db import get_db
from .docker import docker_client, DockerException
from .service import Service
from ..settings import get_settings

__all__ = ["get_services", "Services"]


class Services:
    def __init__(self):
        self.db = get_db()
        self.__services: Dict[str, Service] = {}
        self.__services_by_id: Dict[str, Service] = {}

    def load_services(self):
        services = [
            Service.from_dict(service_dict)
            for service_dict in self.db.services.find({}, {"_id": 0})
        ]
        for service in services:
            self.add(
                service.id,
                service.name,
                service.url,
                service.openapi_dict,
                service.image_name,
                service.environment_vars,
                service.port,
            )

    def _activate(self, service: Service):
        container = docker_client().run_container(
            service.image_name,
            service.environment_vars,
            service.name,
            bind_port=service.port,
        )

    def _stop(self, service: Service):
        docker_client().stop_container(service.name)

    def remove(self, service_id):
        service = self.__services_by_id.pop(service_id, None)
        if service is None:
            return
        self._stop(service)
        self.__services.pop(service.name.lower())

    def add(
            self,
            id: str,
            name: str,
            url: str,
            openapi_dict: dict,
            image_name: str,
            environment_vars: dict,
            port: int,
    ):
        service = Service(id, name, url, openapi_dict, image_name, environment_vars, port)
        try:
            self._activate(service)
        except DockerException as DE:
            if not get_settings().debug:
                raise
            print("Warning: docker error", DE)
            return
        self.__services[service.name.lower()] = service
        self.__services_by_id[service.id] = service

    def get_by_name(self, name) -> Optional[Service]:
        """Get service by lower name (service_name.lower())"""
        return self.__services.get(name)

    def pause(self, id: str):
        service = self.__services_by_id[id]
        docker_client().pause(service.name)

    def unpause(self, id: str):
        service = self.__services_by_id[id]
        docker_client().unpause(service.name)

    def shutdown(self):
        docker_client().stop_all()

    def __iter__(self):
        return iter(self.__services.values())


@lru_cache
def get_services() -> Services:
    return Services()
