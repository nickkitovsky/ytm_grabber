"""Main app module."""

from typing import TYPE_CHECKING, Any, Literal

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, ContentSwitcher, DataTable

from ytm_grabber.core.api_client import ApiClient
from ytm_grabber.core.custom_exceptions import AuthDataError
from ytm_grabber.parser.structures import Endpoint, Playlist
from ytm_grabber.ui.custom_widgets import modal_screens
from ytm_grabber.ui.tabs import DownloadTab, ExploreTab, SettingsTab

if TYPE_CHECKING:
    from pathlib import Path


class YtMusicApp(App):
    CSS_PATH = "app.tcss"

    def __init__(
        self,
        endpoints: list[Endpoint],
    ) -> None:
        self.endpoints: list[Endpoint] = endpoints
        self.app_paths: dict[Literal["auth_files_dir", "download_dir"], str | Path] = {
            "auth_files_dir": "files/auth",
            "download_dir": "files/music",
        }
        self.app_data: dict[Literal["auth_data"], Any] = {
            "auth_data": None,
        }
        self.download_queue: dict[str, Playlist] = {}
        # set app buttons in menu
        self.app_buttons: dict[Literal["settings", "explore", "download", "exit"], Button] = {
            "settings": Button(label="Settings", id="settings_tab", classes="menu_button"),
            "explore": Button(label="Explore", id="explore_tab", classes="menu_button"),
            "download": Button(label="Download", id="download_tab", classes="menu_button"),
            "exit": Button(label="Exit", id="exit_button"),
        }

        self.download_table: DataTable = DataTable(id="download_table")
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Horizontal(
                self.app_buttons["settings"],
                self.app_buttons["explore"],
                self.app_buttons["download"],
                id="buttons",
            ),
            self.app_buttons["exit"],
            classes="height_auto",
        )
        yield ContentSwitcher(
            SettingsTab(id=self.app_buttons["settings"].id),
            ExploreTab(id=self.app_buttons["explore"].id),
            DownloadTab(id=self.app_buttons["download"].id),
            initial=self.app_buttons["settings"].id,
        )

    @on(message_type=Button.Pressed, selector="#exit_button")
    def do_exit(self) -> None:
        self.exit()

    @on(message_type=Button.Pressed, selector=".menu_button")
    def press_menu_button(self, event: Button.Pressed) -> None:
        """Press menu button handler."""
        self.query_one(ContentSwitcher).current = event.button.id
        if str(event.button.id) == self.app_buttons["explore"].id:
            if self.app_data["auth_data"]:
                ApiClient.create_client(self.app_data["auth_data"])
            else:
                self.query_one(ContentSwitcher).current = self.app_buttons["settings"].id
                error_message = "Authdata file not selected.\nSelect authdata file please."
                self.app.push_screen(screen=modal_screens.ShowMessageScreen(message=error_message))
                # msg = "auth data not loaded"
                # raise AuthDataError(msg)
        # elif str(event.button.id) == self.app_buttons["exit"].id:
