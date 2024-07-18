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

def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for a particular function.

    Args:
        method (Callable): The method to be decorated.

    Returns:
        Callable: The wrapped method with call history functionality.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function to store inputs and outputs and call the original method.
        """
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        # Store the inputs
        self._redis.rpush(input_key, str(args))

        # Execute the wrapped method and get the output
        result = method(self, *args, **kwargs)

        # Store the output
        self._redis.rpush(output_key, str(result))

        return result
    return wrapper

def replay(method: Callable):
    """
    Display the history of calls of a particular function.

    Args:
        method (Callable): The method to replay.
    """
    redis_instance = method.__self__._redis
    key = method.__qualname__
    input_key = f"{key}:inputs"
    output_key = f"{key}:outputs"

    input_list = redis_instance.lrange(input_key, 0, -1)
    output_list = redis_instance.lrange(output_key, 0, -1)

    print(f"{key} was called {len(input_list)} times:")
    for input_val, output_val in zip(input_list, output_list):
        print(f"{key}(*{input_val.decode('utf-8')}) -> {output_val.decode('utf-8')}")

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
    @call_history
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
