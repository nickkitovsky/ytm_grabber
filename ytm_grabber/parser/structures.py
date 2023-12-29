"""Response structures."""
from dataclasses import dataclass

from ytm_grabber.core.custom_exceptions import PayloadError
from ytm_grabber.parser.parsers import EndpointParser, PlaylistParser


@dataclass(frozen=True)
class Track:
    artist: str
    title: str
    lenght: str
    video_id: str

    @property
    def full_url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"


class Playlist:
    # TODO: Add verifity payload keys functions.
    def __init__(self, title: str, payload: dict[str, str]) -> None:
        self.title = title
        self.payload = payload
        self._parser = PlaylistParser(self.payload)
        self._tracks = None

    @property
    def tracks(self) -> list[Track]:
        if not self._tracks:
            raw_tracks = self._parser.get_tracks()
            self._tracks = [
                Track(
                    artist=track.get("artist"),
                    title=track.get("title"),
                    lenght=track.get("lenght"),
                    video_id=track.get("video_id"),
                )
                for track in raw_tracks
            ]
        return self._tracks


class Endpoint:
    @classmethod
    def verify_payload(cls, payload: dict) -> None:
        if "browse_id" not in payload:
            msg = "wrong payload keys"
            raise PayloadError(msg)

    def __init__(self, title: str, payload: dict[str, str]) -> None:
        self.verify_payload(payload=payload)
        self.title = title
        self.payload = payload
        self._parser = EndpointParser(endpoint_payload=self.payload)
        self._playlists = None

    @property
    def playlists(self) -> list[Playlist] | list[None]:
        if not self._playlists:
            raw_playlists = self._parser.get_playlists()
            # self._playlists = raw_playlists
            self._playlists = [
                Playlist(
                    title=playlist.get("title"),
                    payload=playlist.get("payload"),
                )
                for playlist in raw_playlists
            ]
        return self._playlists
