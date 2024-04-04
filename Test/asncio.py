import asyncio

async def my_coroutine():
    await asyncio.sleep(5)
    return "Hello, world!"

if __name__ == "__main__":
    new_event_loop = asyncio.new_event_loop()
    result = new_event_loop.run_until_complete(my_coroutine())
