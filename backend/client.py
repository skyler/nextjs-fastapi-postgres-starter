"""Client using the asyncio API."""

import asyncio
from websockets.asyncio.client import connect


async def hello():
    async with connect("ws://localhost:8000/chat") as websocket:
        while True:
            message = input("Message: ")
            await websocket.send(message)
            print(f'Sent "{message}"')
            print("Waiting for next message...")
            response = await websocket.recv()
            print(response)


if __name__ == "__main__":
    asyncio.run(hello())
