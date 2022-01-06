from functools import lru_cache

import redis

from core.settings import get_settings


class Cache:
    def __init__(self):
        self.host = get_settings().redis_host
        self.port = get_settings().redis_port
        self._connection = redis.Redis(host=self.host, port=self.port)

    def get_item(self, key):
        return self._connection.get(key)

    def set_item(self, key, value):
        self._connection.set(key, value)

    def close(self):
        self._connection.close()


@lru_cache
def get_cache() -> Cache:
    return Cache()

