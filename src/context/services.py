from typing import Dict, Optional

from .db import get_db
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
            for service_dict in self.db.services.find({}, {"_id": 0, "created_at": 0})
        ]
        for service in services:
            self.__services[service.prefix_path] = service
            self.__services_by_id[service.id] = service

    def _load_service(self, service_id) -> Service:
        db = get_db()
        service_dict = db.services.find_one({"id": service_id}, {"_id": 0, "created_at": 0})
        return Service.from_dict(service_dict)

    def remove_service(self, service_id):
        service = self.__services_by_id.pop(service_id, None)
        if service is not None:
            self.__services.pop(service.prefix_path)

    def add_service(self, service: Service):
        self.__services[service.prefix_path] = service
        self.__services_by_id[service.id] = service

    # def updated_service(self, service_id):
    #     updated_service = self._load_service(service_id)
    #     old_service = self.__services_by_id[service_id]
    #     self.__services.pop(old_service.prefix_path)
    #     self.__services_by_id[service_id] = updated_service
    #     self.__services[updated_service.prefix_path] = updated_service

    def get_service(self, prefix_path) -> Optional[Service]:
        return self.__services.get(prefix_path)

    def reload(self):
        self.__services.clear()
        self.__services_by_id.clear()
        self._load_services()

    def __iter__(self):
        return iter(self.__services.values())


def get_services() -> Services:
    return Services.get_instance()