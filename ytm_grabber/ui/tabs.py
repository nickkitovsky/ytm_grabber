"""Main tab app widgets."""
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static

from ytm_grabber.ui.custom_widgets import download_widgets, explore_widgets, settings_widgets

if TYPE_CHECKING:
    from ytm_grabber.ui.app import YtMusicApp


class SettingsTab(Static):
    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            settings_widgets.WellcomeWidget(),
            settings_widgets.UserWidget(classes="height_auto"),
            settings_widgets.TypeDownloadDirWidget(),
            classes="height_auto",
        )


class ExploreTab(Static):
    def compose(self) -> ComposeResult:
        self.app: YtMusicApp  # define type for self.app for better work IDE
        yield VerticalScroll(
            *[explore_widgets.EndpointCollapssible(response_structure=endpoint) for endpoint in self.app.endpoints],
        )


class DownloadTab(Static):
    def compose(self) -> ComposeResult:
        yield download_widgets.QueueTable()
