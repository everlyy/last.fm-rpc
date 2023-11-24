from . import Packets
from typing import Callable
import asyncio
import dataclasses
import os
import time
import websockets

send_queue: list[str] = []

@dataclasses.dataclass
class Presence:
    client_id: str
    details: (str | None)
    state: (str | None)
    assets: dict[str, str] | None

class GatewayInterface:
    def __init__(self, ws):
        self._ws = ws

    async def update_presence(self, presence: (Presence | None)):
        global send_queue

        if presence is None:
            print("TODO: Clear presence")
            return

        send_queue.append(Packets.create_packet(
            op=Packets.OpCodes.UPDATE_PRESENCE,
            d=Packets.UpdatePresence(
                since=int(time.time() * 1000),
                activities=[
                    {
                        "name": "last.fm",
                        "type": 2, # "Listening to {name}"
                        "application_id": presence.client_id,
                        "details": presence.details,
                        "state": presence.state,
                        "assets": presence.assets
                    }
                ],
                status="online",
                afk=False
        )))

def panic(message: str):
    print(f"PANIC: {message}")
    os._exit(1)

async def heartbeat(ws, interval):
    while True:
        await asyncio.sleep(interval / 1000.0)
        await ws.send(Packets.create_packet(
            op=Packets.OpCodes.HEARTBEAT,
            d=Packets.Heartbeat()
        ))

async def consume(ws):
    while True:
        print("IN", await ws.recv())

async def _gateway(discord_token: str, on_ready: Callable):
    global send_queue

    gateway_url = "wss://gateway.discord.gg/?v=10&encoding=json"
    async with websockets.connect(gateway_url, max_size=64_000_000) as ws:
        packet = Packets.parse_packet(await ws.recv())

        if isinstance(packet, Packets.Hello):
            print(f"Received HELLO: {packet.heartbeat_interval=}")
            asyncio.create_task(heartbeat(ws, packet.heartbeat_interval))
        else:
            panic("Expected packet with opcode HELLO")

        packet = Packets.create_packet(
            op=Packets.OpCodes.IDENTIFY,
            d=Packets.Identify(
                token=discord_token,
                properties={
                    "os": "linux",
                    "browser": "Everly",
                    "device": "Everly"
                },
                intents=0
            )
        )

        await ws.send(packet)
        packet = Packets.parse_packet(await ws.recv())

        if isinstance(packet, Packets.Ready):
            print(f"Received READY")
        else:
            panic("Expected packet with opcode READY")

        asyncio.create_task(on_ready(GatewayInterface(ws)))
        asyncio.create_task(consume(ws))

        while True:
            if len(send_queue) > 0:
                packet = send_queue.pop()
                print("OUT", packet)
                await ws.send(packet)

            await asyncio.sleep(.1)

def run(discord_token: str, on_ready: Callable):
    asyncio.run(_gateway(discord_token, on_ready))