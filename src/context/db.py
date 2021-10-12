from qwhale_client import APIClient

from context import get_settings


class MongoDB:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if self.__class__._instance is not None:
            raise RuntimeError("Singleton all ready initialized ( use MongoDB.get_instance() )")

        self._client = APIClient(get_settings().qwhale_token)
        self.db = self._client.get_database()
        self.services = self.db.get_collection("services")

    def close(self):
        self._client.close()


def get_db() -> MongoDB:
    return MongoDB.get_instance()
