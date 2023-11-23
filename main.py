from config import *
import pylast
import pypresence
import traceback
import time

class LastFM_RPC:
    def __init__(self, discord_client_id: str, lastfm_username: str, lastfm_api_key: str):
        self._client_id: str = discord_client_id
        self._username: str = lastfm_username
        self._api_key: str = lastfm_api_key
        self._now_playing: pylast.Track | None = None

        self._network: pylast.LastFMNetwork = pylast.LastFMNetwork(api_key=self._api_key)
        self._user: pylast.User = self._network.get_user(self._username)

        self._rpc: pypresence.Presence = pypresence.Presence(self._client_id)
        self._rpc.connect()

    def update(self):
        now_playing: pylast.Track | None = self._user.get_now_playing()

        if self._now_playing == now_playing:
            return

        if now_playing is None:
            self._rpc.clear()
            return

        cover: str | None = None
        if "image" in now_playing.info and len(now_playing.info["image"]) > 0:
                cover = now_playing.info["image"][-1]

        album: str | None = None
        if "album" in now_playing.info and now_playing.info["album"] is not None:
            album = now_playing.info["album"]

        loved: bool = bool(now_playing.get_userloved())

        scrobbles: int = int(self._user.get_playcount())

        print(f"Updating Discord RPC: {now_playing} | {album}")
        try:
            self._rpc.update(
                details=str(now_playing.title),
                state=f"By {now_playing.artist}",

                large_image=cover, # type: ignore
                large_text=album,  # type: ignore

                # Not showing the "loved" icon if there's no cover art because it'll show up
                # really large, which is kinda ugly
                small_image="loved" if loved and cover is not None else None, # type: ignore
                small_text="Loved",

                buttons=[{
                    "label": f"{scrobbles:,} Scrobbles",
                    "url": self._user.get_url()
                }] if SHOW_PROFILE_BUTTON else None # type: ignore
            )
        except pypresence.exceptions.PipeClosed:
            print(f"Discord pipe closed. Attempting reconnection.")
            self._rpc.connect()

        self._now_playing = now_playing

if __name__ == "__main__":
    rpc: LastFM_RPC = LastFM_RPC(
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