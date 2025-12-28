"""Async utilities for running sync vnstock calls in thread pool."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import TypeVar, Callable, Any

# Shared thread pool for all vnstock operations
# vnstock is sync/blocking, so we run it in a thread pool to not block the event loop
_executor = ThreadPoolExecutor(max_workers=12, thread_name_prefix="vnstock_")

T = TypeVar("T")


async def run_sync(func: Callable[..., T], *args, **kwargs) -> T:
    """
    Run a sync function in the thread pool.
    
    Usage:
        result = await run_sync(some_sync_function, arg1, arg2, kwarg1=value)
    """
    loop = asyncio.get_event_loop()
    if kwargs:
        return await loop.run_in_executor(_executor, lambda: func(*args, **kwargs))
    return await loop.run_in_executor(_executor, func, *args)


async def run_parallel(*tasks: Callable[[], T]) -> list[T]:
    """
    Run multiple sync functions in parallel.
    
    Usage:
        results = await run_parallel(
            lambda: func1(arg1),
            lambda: func2(arg2),
        )
    """
    loop = asyncio.get_event_loop()
    futures = [loop.run_in_executor(_executor, task) for task in tasks]
    return await asyncio.gather(*futures, return_exceptions=True)


def async_wrap(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to wrap a sync function to run in thread pool.
    
    Usage:
        @async_wrap
        def sync_function():
            ...
        
        # Now can be called as:
        result = await sync_function()
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await run_sync(func, *args, **kwargs)
    return wrapper


def get_executor() -> ThreadPoolExecutor:
    """Get the shared thread pool executor."""
    return _executor
