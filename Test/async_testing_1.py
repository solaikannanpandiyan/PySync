import asyncio

async def fetch_data(url):
    # Simulate fetching data asynchronously
    await asyncio.sleep(1)
    print("hello")
    return 9

async def main():
    # Get the future
    future = asyncio.create_task(fetch_data('http://example.com/data'))


    # Wait for the future to be completed and get the result
    # await future
    await asyncio.sleep(1)

    # Iterate over the result
    for item in future.__iter__():
        print(item)

if __name__ == "__main__":
    asyncio.run(main())