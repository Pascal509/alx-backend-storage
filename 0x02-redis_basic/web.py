#!/usr/bin/env python3
"""
Module for fetching and caching web pages with expiration and access tracking.
"""

import redis
import requests
from typing import Callable
from functools import wraps

# Initialize Redis client
redis_client = redis.Redis()

def cache_with_expiration(expiration: int = 10):
    """
    Decorator to cache the result of a function call with an expiration time.

    Args:
        expiration (int): The expiration time in seconds for the cache.

    Returns:
        Callable: The wrapped function with caching functionality.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            url = args[0]
            cache_key = f"cache:{url}"
            count_key = f"count:{url}"

            # Increment the access count
            redis_client.incr(count_key)

            # Check if the result is in the cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return cached_result.decode('utf-8')

            # Fetch the result and cache it
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, result)
            return result

        return wrapper
    return decorator

@cache_with_expiration(10)
def get_page(url: str) -> str:
    """
    Fetch the HTML content of a URL and cache the result.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: The HTML content of the URL.
    """
    response = requests.get(url)
    return response.text

if __name__ == "__main__":
    # Example usage
    url = "http://www.example.com"
    print(get_page(url))
    print(get_page(url))  # This should be cached and faster
    print(redis_client.get(f"count:{url}").decode('utf-8'))
