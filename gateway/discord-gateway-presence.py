from config import *
import asyncio
import gateway
import os
import pylast

class LastFM_RPC:
    def __init__(self, discord_client_id: str, lastfm_username: str, lastfm_api_key: str, gateway_interface: gateway.GatewayInterface):
        self._client_id: str = discord_client_id
        self._username: str = lastfm_username
        self._api_key: str = lastfm_api_key
        self._gateway_interface = gateway_interface
        self._now_playing: pylast.Track | None = None

        self._network: pylast.LastFMNetwork = pylast.LastFMNetwork(api_key=self._api_key)
        self._user: pylast.User = self._network.get_user(self._username)

    async def update(self):
        now_playing: pylast.Track | None = self._user.get_now_playing()

        if self._now_playing == now_playing:
            return

        if now_playing is None:
            print("Cleaing Discord RPC")
            await self._gateway_interface.update_presence(None)
            return

        album: str | None = None
        if "album" in now_playing.info and now_playing.info["album"] is not None:
            album = now_playing.info["album"]

        print(f"Updating Discord RPC: {now_playing} | {album}")

        await self._gateway_interface.update_presence(gateway.Presence(
            client_id=self._client_id,
            details=now_playing.title,
            state=f"By {now_playing.artist}",
            assets={
                "large_text": f"On {album}"
            }
        ))
        self._now_playing = now_playing

async def on_ready(gw):
    rpc: LastFM_RPC = LastFM_RPC(
        discord_client_id=DISCORD_CLIENT_ID,
        lastfm_username=LASTFM_USERNAME,
        lastfm_api_key=LASTFM_API_KEY,
        gateway_interface=gw
    )

    while True:
        await rpc.update()
        await asyncio.sleep(UPDATE_TIMEOUT)

if __name__ == "__main__":
    gateway.run(os.environ.get("DISCORD_TOKEN"), on_ready)