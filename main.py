"""Main core file. You can redefine dafault parametrs in app_config, endpoints."""
from ytm_grabber.parser.structures import Endpoint
from ytm_grabber.ui.app import YtMusicApp

default_endpoints = [
    Endpoint(
        title='New releases albums',
        payload={'browse_id': 'FEmusic_new_releases_albums'},
    ),
    Endpoint(
        title='Mixed for you',
        payload={'browse_id': 'FEmusic_mixed_for_you'},
    ),
    Endpoint(
        title='Listen again',
        payload={'browse_id': 'FEmusic_listen_again'},
    ),
    Endpoint(
        title='Library',
        payload={'browse_id': 'FEmusic_library_landing'},
    ),
]

if __name__ == '__main__':
    app = YtMusicApp(endpoints=default_endpoints)
    app.run()
