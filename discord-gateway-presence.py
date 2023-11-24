import asyncio
import websockets
import json
import os
import dataclasses
from typing import Any

class OpCodes:
    READY = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    HELLO = 10

@dataclasses.dataclass
class Packet:
    t: Any
    s: Any
    op: int
    d: Any

@dataclasses.dataclass
class PacketData:
    pass

@dataclasses.dataclass
class Ready(PacketData):
    v: Any
    user_settings_proto: Any
    user_settings: Any
    user_guild_settings: Any
    user: Any
    tutorial: Any
    sessions: Any
    session_type: Any
    session_id: Any
    resume_gateway_url: Any
    relationships: Any
    read_state: Any
    private_channels: Any
    presences: Any
    notification_settings: Any
    notes: Any
    guilds: Any
    guild_join_requests: Any
    guild_experiments: Any
    geo_ordered_rtc_regions: Any
    friend_suggestion_count: Any
    experiments: Any
    current_location: Any
    country_code: Any
    consents: Any
    connected_accounts: Any
    auth_session_id_hash: Any
    auth: Any
    api_code_version: Any
    analytics_token: Any
    _trace: Any

@dataclasses.dataclass
class Heartbeat(PacketData):
    pass

@dataclasses.dataclass
class Identify(PacketData):
    token: str
    properties: dict[str, str]
    intents: int

@dataclasses.dataclass
class Hello(PacketData):
    heartbeat_interval: int
    _trace: list[str]

def parse_packet(data: str) -> (PacketData | None):
    packet = Packet(**json.loads(data))

    with open("packet.json", "w") as file:
        json.dump(dataclasses.asdict(packet), file, indent=2)
        # json.dump(packet.d, file, indent=2)

    if packet.op == OpCodes.HELLO:
        return Hello(**packet.d)

    if packet.op == OpCodes.READY:
        return Ready(**packet.d)

    print(f"tried to parse packet with unhandled opcode {packet.op}")
    print(packet)
    return None

def create_packet(op: int, d: PacketData) -> str:
    packet = Packet(
        t=None,
        s=None,
        op=op,
        d=dataclasses.asdict(d)
    )
    return json.dumps(dataclasses.asdict(packet))

def panic(message: str):
    print(f"PANIC: {message}")
    os._exit(1)

async def heartbeat(ws, interval):
    while True:
        await asyncio.sleep(interval / 1000.0)
        await ws.send(create_packet(
            op=OpCodes.HEARTBEAT,
            d=Heartbeat()
        ))

async def main(discord_token: str):
    gateway_url = "wss://gateway.discord.gg/?v=10&encoding=json"
    async with websockets.connect(gateway_url, max_size=64_000_000) as ws:
        packet = parse_packet(await ws.recv())

        if isinstance(packet, Hello):
            print(f"Received HELLO: {packet.heartbeat_interval=}")
            asyncio.create_task(heartbeat(ws, packet.heartbeat_interval))
        else:
            panic("Expected packet with opcode HELLO")

        packet = create_packet(
            op=OpCodes.IDENTIFY,
            d=Identify(
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
        packet = parse_packet(await ws.recv())

        if isinstance(packet, Ready):
            print(f"Received READY")
        else:
            panic("Expected packet with opcode READY")

        while True:
            print(await ws.recv())

if __name__ == "__main__":
    print("""
        This is an experimental program, it isn't ready for use yet!
        ------
        This version of the RPC is meant to be ran from a different computer so this can run there forever,
        it will show "Listening to last.fm" on your profile and will also work on mobile/browser.
    """)

    discord_token = os.environ.get("DISCORD_TOKEN")
    if discord_token is None:
        print(f"DISCORD_TOKEN not set in environment")
        os._exit(1)

    asyncio.run(main(discord_token))