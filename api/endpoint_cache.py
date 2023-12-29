import time
import functools
from urllib.parse import urlencode
from typing import TypedDict, Union, Callable, List, Any

CACHE_DURATION = 10  # Change to 5 minutes for production


class CachedQuery(TypedDict, total=False):
    data: Any
    timestamp: float


class Cache(TypedDict, total=False):
    query: CachedQuery


def use_cache(
    duration: int = CACHE_DURATION, cache: Cache = {}, length: int = 0
) -> List[Union[Callable[[], Cache], Callable[[Any], Cache]]]:
    """
    Returns a list of functions to get and set cache.
    :param cache: Initial cache
    :param duration: Duration of cache in seconds
    :return: List of functions to get and set cache
    """

    def set_cache(query: str, data: Any) -> Cache:
        nonlocal cache, length
        cache[query] = {"data": data, "timestamp": time.time()}
        length += 1
        if length > 100:
            cache.pop()
            length -= 1
        return cache[query]

    def get_cache(query: str) -> Cache:
        nonlocal cache
        if query in cache and time.time() - cache[query]["timestamp"] < duration:
            return cache[query]
        return {}

    return [get_cache, set_cache]


def check_cache(*args, **kwargs):
    """
    Decorator to check cache before making a request.
    :param args: Positional arguments for use_cache
    :param kwargs: Keyword arguments for use_cache
    :return: Decorator
    """

    get_cache, set_cache = args[0]  # This is a use_cache() instance

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            query = urlencode(kwargs)
            cache = get_cache(query)
            if cache:
                return cache["data"]
            response = func(*args, **kwargs)
            set_cache(query, response)
            return response

        return wrapper

    return decorator
