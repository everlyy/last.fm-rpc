from config import *
import pylast
import pypresence
import traceback
import time

class LastFM_RPC:
    def __init__(self, discord_client_id, lastfm_username, lastfm_api_key):
        self._client_id = discord_client_id
        self._username = lastfm_username
        self._api_key = lastfm_api_key

        self._network = pylast.LastFMNetwork(api_key=self._api_key)
        self._user = self._network.get_user(self._username)

        self._rpc = pypresence.Presence(self._client_id)
        self._rpc.connect()

    def update(self):
        now_playing = self._user.get_now_playing()

        if now_playing is None:
            self._rpc.clear()
            return

        cover = None
        if "image" in now_playing.info and len(now_playing.info["image"]) > 0:
                cover = now_playing.info["image"][-1]

        album = None
        if "album" in now_playing.info and now_playing.info["album"] is not None:
            album = now_playing.info["album"]

        try:
            self._rpc.update(
                details=str(now_playing.title),
                state=f"By {now_playing.artist}",
                large_image=cover,
                large_text=album
            )
        except pypresence.exceptions.PipeClosed:
            print(f"Discord pipe closed. Attempting reconnection.")
            self._rpc.connect()

if __name__ == "__main__":
    rpc = LastFM_RPC(
        discord_client_id=DISCORD_CLIENT_ID,
        lastfm_username=LASTFM_USERNAME,
        lastfm_api_key=LASTFM_API_KEY
    )

    while True:
        try:
            rpc.update()
        except Exception:
            traceback.print_exc()

        time.sleep(UPDATE_TIMEOUT)
