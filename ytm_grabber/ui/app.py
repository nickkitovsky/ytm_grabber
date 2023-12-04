"""Main app module."""

from typing import TYPE_CHECKING, Any, Literal

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, ContentSwitcher, DataTable

from ytm_grabber.core.api_client import ApiClient
from ytm_grabber.parser.structures import Endpoint, Playlist
from ytm_grabber.ui.tabs import DownloadTab, ExploreTab, SettingsTab

if TYPE_CHECKING:
    from pathlib import Path


class YtMusicApp(App):
    CSS_PATH = 'app.tcss'

    def __init__(
        self,
        endpoints: list[Endpoint],
    ):
        self.endpoints: list[Endpoint] = endpoints
        self.app_paths: dict[Literal['auth_files_dir', 'download_dir'], str | Path] = {
            'auth_files_dir': 'files/auth',
            'download_dir': 'files/music',
        }
        self.app_data: dict[Literal['auth_data'], Any] = {
            'auth_data': None,
        }
        self.download_queue: dict[str, Playlist] = {}
        # set app buttons in menu
        self.app_buttons: dict[Literal['settings', 'explore', 'download'], Button] = {
            'settings': Button(label='Settings', id='settings_tab', classes='menu_button'),
            'explore': Button(label='Explore', id='explore_tab', classes='menu_button'),
            'download': Button(label='Download', id='download_tab', classes='menu_button'),
        }
        self.download_table: DataTable = DataTable(id='download_table')
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Horizontal(
            self.app_buttons['settings'],
            self.app_buttons['explore'],
            self.app_buttons['download'],
            id='buttons',
        )

        yield ContentSwitcher(
            SettingsTab(id=self.app_buttons['settings'].id),
            ExploreTab(id=self.app_buttons['explore'].id),
            DownloadTab(id=self.app_buttons['download'].id),
            initial=self.app_buttons['settings'].id,
        )

    @on(message_type=Button.Pressed, selector='.menu_button')
    def press_menu_button(self, event: Button.Pressed) -> None:
        """Press menu button handler."""
        self.query_one(ContentSwitcher).current = event.button.id
        if str(event.button.id) == self.app_buttons['explore'].id:
            if self.app_data['auth_data']:
                ApiClient.create_client(self.app_data['auth_data'])
            else:
                raise ValueError('auth data not loaded')
