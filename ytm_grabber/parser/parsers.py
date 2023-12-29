"""Parsers for response."""
from typing import Any

from ytm_grabber.core.api_client import ApiClient
from ytm_grabber.parser.chains import EndpointContentsChain, EndpointPayloadChains, PlaylistContentsChain
from ytm_grabber.parser.common_utils import extract_chain, extract_runs


class EndpointParser:
    def __init__(self, endpoint_payload: dict[str, str]) -> None:
        self.URL = "https://music.youtube.com/youtubei/v1/browse"
        self.endpoint_payload = endpoint_payload
        self.contents_chain = EndpointContentsChain
        self.payload_chains = EndpointPayloadChains

    def get_playlists(self) -> dict[Any, Any]:
        response = self.fetch_content()
        return self.parse_playlists(raw_response=response)

    def fetch_content(self) -> dict[Any, Any] | None:
        client = ApiClient.get_exist_client()
        return client.send_request(self.endpoint_payload, url=self.URL)

    def parse_playlists(self, raw_response: dict) -> list[dict]:
        """Parse response from api.

        Args:
        ----
            raw_response (dict): raw response from api

        Returns:
        -------
            list[dict]: list of data contains in endpoint (list of playlists)
        """
        parsed_data = []
        # using contents_chain without loop, while it one.
        playlists = extract_chain(json_obj=raw_response, chain=self.contents_chain.common_cases.chain)
        for playlist in playlists:
            playlist = extract_chain(playlist)
            parsed_data.append(self._parse_playlist(playlist))
        return parsed_data

    def _parse_playlist(self, raw_playlist_data: dict) -> dict:
        """Parse raw playlist data, and extract title and payload.

        Args:
        ----
            raw_playlist_data (dict): raw response data of playlist item

        Returns:
        -------
            dict: title and payload for current playlist
        """
        return {
            "title": self._parse_playlist_title(raw_content_item=raw_playlist_data),
            "payload": self._parse_playlist_payload(raw_content_item=raw_playlist_data),
        }

    def _parse_playlist_title(self, raw_content_item: dict) -> str:
        title = extract_runs(runs_list=raw_content_item["title"]["runs"]).strip()
        try:
            subtitle = extract_runs(runs_list=raw_content_item["subtitle"]["runs"]).strip()
        except KeyError:
            item_title = title
        else:
            item_title = f"{title} ({subtitle})"
        return item_title

    def _parse_playlist_payload(self, raw_content_item: dict):
        for current_chain in self.payload_chains:
            try:
                payload = extract_chain(
                    json_obj=raw_content_item,
                    chain=current_chain.chain,
                )

            except KeyError:
                continue
            return {key: value for key, value in payload.items() if key in current_chain.return_keys}
        return None


class PlaylistParser:
    def __init__(self, playlist_payload: dict[str, str]) -> None:
        self.URL = "https://music.youtube.com/youtubei/v1/next"
        self.contents_chain = PlaylistContentsChain
        self.playlist_payload = playlist_payload

    def fetch_content(self) -> dict[Any, Any] | None:
        client = ApiClient.get_exist_client()
        return client.send_request(self.playlist_payload, url=self.URL)

    def get_tracks(self) -> list[dict[str, str]]:
        response = self.fetch_content()
        return self.parse_tracks(raw_response=response)

    def parse_tracks(self, raw_response: dict) -> list[dict[str, str]]:
        """Parse raw tracks data.

        Args:
        ----
            raw_response (dict): raw response from api

        Returns:
        -------
            list[dict[str, str]]: list of track data (artist, title, youtube id, track lenght)
        """
        parsed_data = []
        # using contents_chain without loop, while it one.
        tracks = extract_chain(json_obj=raw_response, chain=self.contents_chain.common_cases.chain)
        for track in tracks:
            track = extract_chain(json_obj=track)
            try:
                parsed_data.append(self._parse_track(raw_track_data=track))
            except KeyError:
                continue
        return parsed_data

    def _parse_track(self, raw_track_data: dict) -> dict[str, str]:
        """Parse raw track data.

        Args:
        ----
            raw_track_data (dict): raw track data

        Returns:
        -------
            dict[str, str]: artist, title, track lenght, youtube id for current track
        """
        return {
            "artist": self._parse_artist(raw_track_data=raw_track_data),
            "title": self._parse_title(raw_track_data=raw_track_data),
            "lenght": self._parse_lenght(raw_track_data=raw_track_data),
            "video_id": self._parse_video_id(raw_track_data=raw_track_data),
        }

    def _parse_title(self, raw_track_data: dict) -> str:
        return extract_runs(runs_list=raw_track_data["title"]["runs"]).strip()

    def _parse_lenght(self, raw_track_data: dict) -> str:
        return extract_runs(runs_list=raw_track_data["lengthText"]["runs"]).strip()

    def _parse_video_id(self, raw_track_data: dict) -> str:
        return raw_track_data["videoId"]

    def _parse_artist(self, raw_track_data: dict) -> str:
        track_data = raw_track_data["longBylineText"]["runs"]
        artist = []
        for field in track_data:
            if field.get("navigationEndpoint") and self._is_artist_field(field):
                artist.append(field["text"])
        return ", ".join(artist) if artist else track_data[0]["text"]

    def _is_artist_field(self, field: dict) -> bool:
        field_type = extract_chain(
            json_obj=field,
            chain=(
                "navigationEndpoint",
                "browseEndpoint",
                "browseEndpointContextSupportedConfigs",
                "pageType",
            ),
        )
        return field_type == "MUSIC_PAGE_TYPE_ARTIST"
