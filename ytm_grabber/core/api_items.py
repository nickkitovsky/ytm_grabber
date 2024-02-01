"""Module contains classes of API items."""
import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ytm_grabber.core.api_client import ApiClient
from ytm_grabber.core.custom_exceptions import ExistingClientNotFoundError


@dataclass(frozen=True)
class Track:
    artist: str
    title: str
    lenght: str
    video_id: str

    @property
    def full_url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"


class AbstractItem(ABC):
    def __init__(
        self,
        payload: dict[str, str],
        title: str | None = None,
        url: str = "https://music.youtube.com/youtubei/v1/browse",
    ) -> None:
        self.url = url
        self.payload = payload
        self.title = title
        self.children: list = []
        self._client = ApiClient.get_exist_client()

    def fetch_response(self) -> dict[typing.Any, typing.Any] | list | None:
        if self._client:
            return self._client.send_request(self.payload, url=self.url)
        raise ExistingClientNotFoundError

    @abstractmethod
    def parse(self, raw_response: dict | str | list) -> None:
        pass


class Endpoint(AbstractItem):
    def parse(self, raw_response: dict | str | list) -> None:
        pass
