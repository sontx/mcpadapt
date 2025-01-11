import asyncio
from contextlib import asynccontextmanager
import threading
from functools import wraps
from typing import Any, Callable, Coroutine


def async_to_sync(
    async_func: Callable[..., Coroutine[Any, Any, Any]],
) -> Callable[..., Any]:
    """Convert an async function to a sync function in an async context.

    This is usually not recommended, but tools are expected to be synchronous for
    for example in smolagents.

    This is done by using a separate thread to avoid blocking the asyncio event loop.
    """

    @wraps(async_func)
    def sync_wrapper(*args, **kwargs):
        result = None
        error = None

        def run_async():
            nonlocal result, error
            try:
                print("running async")
                result = asyncio.run(async_func(*args, **kwargs))
            except Exception as e:
                error = e

        # run in a separate thread to avoid blocking the event loop
        print("starting thread")
        thread = threading.Thread(target=run_async)
        thread.start()
        print("joining thread")
        thread.join(timeout=10)
        print("joined thread")
        if error:
            raise error
        return result

    return sync_wrapper


if __name__ == "__main__":

    @asynccontextmanager
    async def some_function():
        async def call_tool(a):
            await asyncio.sleep(10)
            return a

        yield call_tool

    async def main():
        async with some_function() as call_tool:
            response = async_to_sync(call_tool)(1)
            print(response)

    asyncio.run(main())
