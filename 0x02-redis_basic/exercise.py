#!/usr/bin/env python3
"""
Module for interacting with Redis for caching purposes.
"""

import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps

def count_calls(method: Callable) -> Callable:
    """
    Decorator to count the number of calls to a method.

    Args:
        method (Callable): The method to be decorated.

    Returns:
        Callable: The wrapped method with call count functionality.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function to increment the call count and call the original method.
        """
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper

class Cache:
    """
    Cache class for storing and retrieving data from Redis.
    """

    def __init__(self):
        """
        Initialize the Cache instance and flush the Redis database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a randomly generated key.

        Args:
            data (Union[str, bytes, int, float]): Data to be stored in Redis.

        Returns:
            str: The randomly generated key used to store the data.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis and optionally apply a conversion function.

        Args:
            key (str): The key for the data in Redis.
            fn (Optional[Callable]): Optional function to convert the data back to the desired format.

        Returns:
            Union[str, bytes, int, float, None]: The retrieved data or None if the key does not exist.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve a string from Redis.

        Args:
            key (str): The key for the data in Redis.

        Returns:
            Optional[str]: The retrieved string or None if the key does not exist.
        """
        return self.get(key, lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve an integer from Redis.

        Args:
            key (str): The key for the data in Redis.

        Returns:
            Optional[int]: The retrieved integer or None if the key does not exist.
        """
        return self.get(key, int)
