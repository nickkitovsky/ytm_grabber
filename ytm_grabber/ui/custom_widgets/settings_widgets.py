"""Settions widgets."""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.validation import Function, ValidationResult
from textual.widgets import Button, Input, Label, Markdown, Select, Static

from ytm_grabber.core import authdata
from ytm_grabber.core.custom_exceptions import ParsingError
from ytm_grabber.ui.custom_widgets import modal_screens

if TYPE_CHECKING:
    from ytm_grabber.ui.app import YtMusicApp


class UserWidget(Static):
    def __init__(self, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(id=id, classes=classes)
        self.app: YtMusicApp  # define type for self.app for better work IDE
        self.new_user_widget = NewUserWidget(classes="height_auto")
        self.select_user_widget = SelectUserWidget(classes="height_auto", id="select_widget")

    def compose(self) -> ComposeResult:
        yield Vertical(
            self.new_user_widget,
            self.select_user_widget,
            classes="height_auto",
        )

    @on(message_type=Button.Pressed, selector="#add_auth_file_button")
    def _add_new_auth_file(self) -> None:
        def dump_clipboard_data(filename: str) -> None:
            new_user.dump_authdata(filename=filename, authfiles_dir=self.app.app_paths["auth_files_dir"])
            self._refresh_select_widget()

        try:
            new_user = authdata.AuthDataParser.read_from_clipboard()
        except ParsingError:
            error_message = "Clipboard content does not match cURL request.\nSee the instruction please."
            self.app.push_screen(screen=modal_screens.ShowMessageScreen(message=error_message))
        else:
            self.app.push_screen(modal_screens.TypeFilenameScreen(), dump_clipboard_data)

    def _refresh_select_widget(self) -> None:
        select_user_widget = self.query_one("#select_user_widget")
        if isinstance(select_user_widget, Select):
            select_widget_content = self.select_user_widget.get_select_widget_content()
            select_user_widget.set_options(select_widget_content["options_list"])
            select_user_widget.disabled = select_widget_content["disabled_flag"]


class NewUserWidget(Static):
    def __init__(self, classes: str = "height_auto") -> None:
        super().__init__(classes=classes)
        self.app: YtMusicApp  # define type for self.app for better work IDE

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label(renderable="Add user", classes="label_text"),
            Button(
                label="Click here to add new authfile from clipboard",
                variant="warning",
                classes="height_auto",
                id="add_auth_file_button",
            ),
            classes="height_auto",
        )


class SelectUserWidget(Static):
    """Select authdata user file."""

    def __init__(self, id: str | None = None, classes: str | None = "height_auto") -> None:
        super().__init__(id=id, classes=classes)
        self.app: YtMusicApp  # define type for self.app for better work IDE

    def compose(self) -> ComposeResult:
        options = self.get_select_widget_content()

        yield Horizontal(
            Label(renderable="Select user", classes="label_text"),
            Select(
                id="select_user_widget",
                options=options["options_list"],
                allow_blank=False,
                value=options["options_list"][-1][1],
                disabled=options["disabled_flag"],
            ),
            classes="height_auto width_90percent",
        )

    def get_select_widget_content(self) -> dict[Literal["options_list", "disabled_flag"], Any]:
        self.authdata_files = self.read_authdata_files()
        if self.authdata_files:
            options_list = tuple((line, line) for line in self.authdata_files)
            disabled_flag = False
            # load default auth_data to app (last entry).
            self.app.app_data["auth_data"] = self.authdata_files[options_list[-1][1]]
        else:
            options_list = (("Any authfile not found. Please add it.", "notfound"),)
            disabled_flag = True
        return {"options_list": options_list, "disabled_flag": disabled_flag}

    def read_authdata_files(self) -> dict[str, authdata.AuthData]:
        return authdata.AuthDataParser.scan_dir(dir_path=self.app.app_paths["auth_files_dir"])

    @on(Select.Changed)
    def _select_changed(self, event: Select.Changed) -> None:
        selected_value = str(event.value)
        self.app.app_data["auth_data"] = self.authdata_files[selected_value]


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
        if isinstance(event.validation_result, ValidationResult):
            if event.validation_result.is_valid:
                self._validation_label.update("")
            else:
                self._validation_label.update(event.validation_result.failure_descriptions[0])

    @on(message_type=Input.Changed)
    def _set_download_dir(self, event: Input.Submitted) -> None:
        self.app.app_paths["download_dir"] = event.value

    def _is_dir(self, typed_path: str) -> bool:
        return Path(typed_path).is_dir()
