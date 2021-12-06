from functools import lru_cache

from pymongo import MongoClient

from core.settings import get_settings


class MongoDB:
    def __init__(self):
        self._client = MongoClient(get_settings().mongo_url)
        self.db = self._client.get_database("gateway")
        self.services = self.db.get_collection("services")

    def close(self):
        self._client.close()


@lru_cache
def get_db() -> MongoDB:
    return MongoDB()
