"""Settinhs widgets."""
from pathlib import Path
from typing import TYPE_CHECKING

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.validation import Function, ValidationResult
from textual.widgets import Input, Label, Markdown, Select, Static

from ytm_grabber.core import auth_data

if TYPE_CHECKING:
    from ytm_grabber.ui.app import YtMusicApp


class SelectUserWidget(Static):
    """Select authdata user file."""

    def compose(self) -> ComposeResult:
        self.app: YtMusicApp  # define type for self.app for better work IDE
        # unpacking two values for load authdata once
        default_authdata, self.authdata = self.load_authdata()
        with Horizontal(classes='height_auto width_90percent'):
            yield Label(renderable='Select user', classes='label_text')

            yield Select(
                options=((line, line) for line in self.authdata),
                allow_blank=False,
                value=default_authdata,
            )

    def load_authdata(self) -> tuple[str, dict[str, auth_data.AuthData]]:
        authdata_files = auth_data.load_authdata_from_dir(self.app.app_paths['auth_files_dir'])
        auth_files_keys = tuple(authdata_files)
        # set first entry by default
        if authdata_files:
            default_authdata_file = auth_files_keys[0]
            self.app.app_data['auth_data'] = authdata_files[default_authdata_file]
            return default_authdata_file, authdata_files
        raise ValueError('any auth files not found')

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        selected_value = str(event.value)
        self.app.app_data['auth_data'] = self.authdata[selected_value]


class WellcomeWidget(Static):
    """Widget with wellcome text on top in the app."""

    def compose(self) -> ComposeResult:
        yield Markdown(self._read_wellcome_text())

    def _read_wellcome_text(self) -> str:
        wellcome_text_file = 'ytm_grabber/ui/custom_widgets/wellcome_text.md'
        with open(file=wellcome_text_file, mode='r', encoding='utf-8') as file_content:
            return file_content.read()


class TypeDownloadDirWidget(Static):
    """Widget for select download dir path."""

    def compose(self) -> ComposeResult:
        self.app: YtMusicApp  # define type for self.app for better work IDE
        self._validation_label = Label('', id='validation_result')
        with Horizontal(classes='height_auto width_90percent'):
            yield Label(renderable='Enter path', classes='label_text')
            with Vertical(classes='height_auto'):
                yield Input(
                    placeholder='Enter a dir path to download music or `files/music` dir default',
                    validators=[
                        Function(self._is_dir, 'Value is not dir.'),
                    ],
                )
                yield self._validation_label

    @on(Input.Changed)
    def _show_invalid_reasons(self, event: Input.Changed) -> None:
        # Updating the UI to show the reasons why validation failed
        if isinstance(event.validation_result, ValidationResult) and event.validation_result.is_valid:
            self._validation_label.update('')
        else:
            self._validation_label.update(event.validation_result.failure_descriptions[0])

    @on(message_type=Input.Changed)
    def _set_download_dir(self, event: Input.Submitted) -> None:
        self.app.app_paths['download_dir'] = event.value

    def _is_dir(self, typed_path: str) -> bool:
        return Path(typed_path).is_dir()
