"""Chain for parsing responses."""

import enum


class EndpointPayloadChains(enum.Enum):
    listen_again = {
        'chain': ('menu', 'items', 0, 'navigationEndpoint', 'watchEndpoint'),
        'return_keys': ('params', 'videoId'),
    }
    common_cases = {
        'chain': ('menu', 'items', 0, 'navigationEndpoint', 'watchPlaylistEndpoint'),
        'return_keys': ('params', 'playlistId'),
    }

    def __init__(self, chain_data) -> None:
        self.chain = chain_data['chain']
        self.return_keys = chain_data['return_keys']


class EndpointContentsChain(enum.Enum):
    common_cases = {
        'chain': ('contents', 'content', 'contents', 'items'),
    }

    def __init__(self, chain_data) -> None:
        self.chain = chain_data['chain']


class PlaylistContentsChain(enum.Enum):
    common_cases = {
        'chain': ('contents', 0, 'content', 'content', 'contents'),
    }

    def __init__(self, chain_data) -> None:
        self.chain = chain_data['chain']
