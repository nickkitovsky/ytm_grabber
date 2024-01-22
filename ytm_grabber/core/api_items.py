"""Module contains classes of API items."""
import typing
from dataclasses import dataclass

from ytm_grabber.core.api_client import ApiClient


@dataclass(frozen=True)
class Track:
    artist: str
    title: str
    lenght: str
    video_id: str

    @property
    def full_url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"


class Endpoint:
    def __init__(self, payload: dict[str, str], title: str | None = None) -> None:
        self._url = "https://music.youtube.com/youtubei/v1/browse"
        self.payload = payload
        self.title = title
        self.children: list = []
        self._client = ApiClient.get_exist_client()

    def fetch_children(self) -> dict[typing.Any, typing.Any] | list | None:
        return self._client.send_request(self.payload, url=self._url)
