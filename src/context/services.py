from typing import Dict, Optional

from .db import get_db
from .docker import docker_client
from models.service import Service

__all__ = ["get_services", "Services"]


class Services:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if self._instance is not None:
            raise RuntimeError("Services singleton all ready initiated")

        self.db = get_db()
        self.__services: Dict[str, Service] = {}
        self.__services_by_id: Dict[str, Service] = {}
        self._load_services()

    def _load_services(self):
        services = [
            Service.from_dict(service_dict)
            for service_dict in self.db.services.find({}, {"_id": 0})
        ]
        for service in services:
            self.add_service(
                service.id,
                service.name,
                service.url,
                service.openapi_dict,
                service.image_name,
                service.environment_vars
            )

    def _activate_service(self, service: Service):
        container = docker_client().run_container(service.image_name, service.environment_vars, service.name)

    def _stop_service(self, service: Service):
        docker_client().stop_container(service.name)

    def remove_service(self, service_id):
        service = self.__services_by_id.pop(service_id, None)
        if service is None:
            return
        self._stop_service(service)
        self.__services.pop(service.prefix_path)
        self.__services_by_id.pop(service.id)

    def add_service(
            self,
            id: str,
            name: str,
            url: str,
            openapi_dict: dict,
            image_name: str,
            environment_vars: dict,
    ):
        service = Service(id, name, url, openapi_dict, image_name, environment_vars)
        self._activate_service(service)
        self.__services[service.prefix_path] = service
        self.__services_by_id[service.id] = service

    # def updated_service(self, service_id):
    #     updated_service = self._load_service(service_id)
    #     old_service = self.__services_by_id[service_id]
    #     self.__services.pop(old_service.prefix_path)
    #     self.__services_by_id[service_id] = updated_service
    #     self.__services[updated_service.prefix_path] = updated_service

    def get_service_by_prefix_path(self, prefix_path) -> Optional[Service]:
        return self.__services.get(prefix_path)

    def shutdown(self):
        docker_client().stop_all()

    def __iter__(self):
        return iter(self.__services.values())


def get_services() -> Services:
    return Services.get_instance()
