from pymongo import MongoClient

from ...core.settings import get_settings

__all__ = ["get_db"]


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

        self._client = MongoClient(get_settings().mongo_url)
        self.db = self._client.get_database()
        self.tokens = self.db.get_collection("tokens")

    def close(self):
        self._client.close()


def get_db() -> MongoDB:
    return MongoDB.get_instance()
