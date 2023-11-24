from typing import Any
import dataclasses
import json

class OpCodes:
    READY = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    UPDATE_PRESENCE = 3
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
class UpdatePresence(PacketData):
    since: int | None
    activities: list
    status: str
    afk: bool

@dataclasses.dataclass
class Hello(PacketData):
    heartbeat_interval: int
    _trace: list[str]

def parse_packet(data: str) -> (PacketData | None):
    packet = Packet(**json.loads(data))

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