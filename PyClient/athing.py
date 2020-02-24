import asyncio

async def greet_every_two_seconds():
    while True:
        print('Hello World')
        await asyncio.sleep(2)


async def someFunction():
    # run in main thread (Ctrl+C to cancel)
    await greet_every_two_seconds()

# run in background
#asyncio.create_task(greet_every_two_seconds())

asyncio.create_task(someFunction())

