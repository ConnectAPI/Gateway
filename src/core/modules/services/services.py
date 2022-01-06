from typing import Dict, Optional
from functools import lru_cache

from core.modules.db import get_db
from .service import Service
from .docker import docker_client

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
            service.activate()

    def add(
            self,
            id: str,
            name: str,
            url: str,
            openapi_dict: dict,
            image_name: str,
            environment_vars: dict
    ):
        service = Service(id, name, url, openapi_dict, image_name, environment_vars)
        service.activate()
        self.__services[service.name.lower()] = service
        self.__services_by_id[service.id] = service

    def remove(self, service_id):
        service = self.__services_by_id.pop(service_id, None)
        if service is None:
            return
        service.deactivate()
        self.__services.pop(service.name.lower())

    def get_by_name(self, name) -> Optional[Service]:
        """Get service by lower name (service_name.lower())"""
        return self.__services.get(name)

    def pause(self, service_id: str):
        service = self.__services_by_id[service_id]
        service.pause()

    def unpause(self, service_id: str):
        service = self.__services_by_id[service_id]
        service.unpause()

    def shutdown(self):
        docker_client().stop_all()

    def __iter__(self):
        return iter(self.__services.values())


@lru_cache
def get_services() -> Services:
    return Services()
