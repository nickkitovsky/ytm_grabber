"""Settinhs widgets."""
from pathlib import Path
from typing import TYPE_CHECKING

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.validation import Function, ValidationResult
from textual.widgets import Button, Input, Label, Markdown, Select, Static

from ytm_grabber.core import authdata, custom_exceptions

if TYPE_CHECKING:
    from textual.widget import Widget

    from ytm_grabber.ui.app import YtMusicApp


class SelectUserWidget(Static):
    """Select authdata user file."""

    def __init__(self, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(id=id, classes=classes)
        self.app: YtMusicApp  # define type for self.app for better work IDE
        self.select_user_authfile_widget: Widget
        try:
            self.authdata = self.load_authdata()
        except custom_exceptions.AuthFilesError:
            self.select_user_authfile_widget = Button(
                label="CLICK HERE TO ADD NEW AUTH FILE FROM CLIPBOARD",
                variant="warning",
                classes="height_auto",
                id="add_auth_file_button",
            )
        else:
            self.select_user_authfile_widget = Select(
                options=((line, line) for line in self.authdata),
                allow_blank=False,
                value=self._get_first_authfile(authdata_files=self.authdata),
            )

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label(renderable="Select user", classes="label_text"),
            self.select_user_authfile_widget,
            classes="height_auto width_90percent",
        )

    def load_authdata(self) -> dict[str, authdata.AuthData]:
        """Read and parse files in app_paths['auth_files_dir'].

        Raises
        ------
            custom_exceptions.AuthFilesError: not found any authfile

        Returns
        -------
            dict[str, auth_data.AuthData]: {filename: AuthData}
        """
        authdata_files = authdata.get_authdata_from_dir(dir_path=self.app.app_paths["auth_files_dir"])
        if authdata_files:
            return authdata_files
        msg = "any auth files not found"
        raise custom_exceptions.AuthFilesError(msg)

    def _get_first_authfile(self, authdata_files: dict[str, authdata.AuthData]) -> str:
        """Return first filename in authdata_files.

        Args:
        ----
            authdata_files (dict[str, auth_data.AuthData]): dict of {filename:AuthData}

        Returns:
        -------
            str: first AuthData file name
        """
        return next(iter(authdata_files))

    @on(Select.Changed)
    def _select_changed(self, event: Select.Changed) -> None:
        selected_value = str(event.value)
        self.app.app_data["auth_data"] = self.authdata[selected_value]

    @on(message_type=Button.Pressed, selector="#add_auth_file_button")
    def _add_new_auth_file(self) -> None:
        pass


class WellcomeWidget(Static):
    """Widget with wellcome text on top in the app."""

    def compose(self) -> ComposeResult:
        yield Markdown(self._read_wellcome_text())

    def _read_wellcome_text(self) -> str:
        wellcome_text_file = "ytm_grabber/ui/custom_widgets/wellcome_text.md"
        with open(file=wellcome_text_file, encoding="utf-8") as file_content:
            return file_content.read()


class TypeDownloadDirWidget(Static):
    """Widget for select download dir path."""

    def compose(self) -> ComposeResult:
        self.app: YtMusicApp  # define type for self.app for better work IDE
        self._validation_label = Label("", id="validation_result")
        with Horizontal(classes="height_auto width_90percent"):
            yield Label(renderable="Enter path", classes="label_text")
            with Vertical(classes="height_auto"):
                yield Input(
                    placeholder="Enter a dir path to download music or `files/music` dir default",
                    validators=[
                        Function(self._is_dir, "Value is not dir."),
                    ],
                )
                yield self._validation_label

    @on(Input.Changed)
    def _show_invalid_reasons(self, event: Input.Changed) -> None:
        # Updating the UI to show the reasons why validation failed
        if isinstance(event.validation_result, ValidationResult) and event.validation_result.is_valid:
            self._validation_label.update("")
        else:
            self._validation_label.update(event.validation_result.failure_descriptions[0])

    @on(message_type=Input.Changed)
    def _set_download_dir(self, event: Input.Submitted) -> None:
        self.app.app_paths["download_dir"] = event.value

    def _is_dir(self, typed_path: str) -> bool:
        return Path(typed_path).is_dir()
