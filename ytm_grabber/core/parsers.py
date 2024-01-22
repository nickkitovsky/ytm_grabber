"""Parsers for API responses."""

endpoint_children_payload_chains = [
    {
        "chain": ("menu", "items", 0, "navigationEndpoint", "watchEndpoint"),
        "return_keys": ("params", "videoId"),
    },
    {
        "chain": ("menu", "items", 0, "navigationEndpoint", "watchPlaylistEndpoint"),
        "return_keys": ("params", "playlistId"),
    },
]
endpoint_children_contents_chains = [
    {
        "chain": ("contents", "content", "contents", "items"),
    },
]


def endpoint_parser(raw_response: dict | list):
    parsed_data = []
    # using contents_chain without loop, while it one.
    playlists = extract_chain(json_obj=raw_response, chain=self.contents_chain.common_cases.chain)
    for playlist in playlists:
        playlist = extract_chain(playlist)
        parsed_data.append(self._parse_playlist(playlist))
    return parsed_data

    # def _parse_playlist(self, raw_playlist_data: dict) -> dict:
    #     """Parse raw playlist data, and extract title and payload.

    #     Args:
    #     ----
    #         raw_playlist_data (dict): raw response data of playlist item

    #     Returns:
    #     -------
    #         dict: title and payload for current playlist
    #     """
    #     return {
    #         "title": self._parse_playlist_title(raw_content_item=raw_playlist_data),
    #         "payload": self._parse_playlist_payload(raw_content_item=raw_playlist_data),
    #     }

    # def _parse_playlist_title(self, raw_content_item: dict) -> str:
    #     title = extract_runs(runs_list=raw_content_item["title"]["runs"]).strip()
    #     try:
    #         subtitle = extract_runs(runs_list=raw_content_item["subtitle"]["runs"]).strip()
    #     except KeyError:
    #         item_title = title
    #     else:
    #         item_title = f"{title} ({subtitle})"
    #     return item_title

    # def _parse_playlist_payload(self, raw_content_item: dict):
    #     for current_chain in self.payload_chains:
    #         try:
    #             payload = extract_chain(
    #                 json_obj=raw_content_item,
    #                 chain=current_chain.chain,
    #             )

    #         except KeyError:
    #             continue
    #         return {key: value for key, value in payload.items() if key in current_chain.return_keys}
    #     return None
