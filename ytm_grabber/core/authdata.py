"""Module for working with auth files."""
import json
import shlex
from pathlib import Path
from typing import Self
from urllib.parse import parse_qsl, urlsplit

import pyperclip  # type: ignore[import-untyped]


class DumpAuthFileError(Exception):
    """Curl file content not found."""


class ParsingError(Exception):
    """Error of parsing data."""


class AuthData:
    """Data for authentification on Youtube Music."""

    def __init__(self, raw_curl_content: list[str]) -> None:
        self.headers: dict = {}
        self.params: dict = {}
        self.json_data: dict = {}
        self.raw_curl_content = raw_curl_content
        if "^" in self.raw_curl_content[0]:
            self.raw_curl_content = self._fix_cmd_break_lines(content_with_cr=raw_curl_content)
        try:
            self._parse_authdata()
        except (IndexError, json.JSONDecodeError) as exc:
            msg = "error of parse curl_data"
            raise ParsingError(msg) from exc

    @classmethod
    def read_from_file(cls, curl_file: str | Path) -> Self:
        """Read file from browser, with your session from Dev tools, and then 'copy as cURL'.

        Args:
        ----
            curl_file (str | Path): Path to file

        Raises:
        ------
            TypeError: Wrong type. You must pass str or Path object
            FileNotFoundError: Wrong file path

        Returns:
        -------
            Self(AuthData): AuthData instance.
        """
        if not isinstance(curl_file, (str, Path)):
            msg = "Incorrect type of `curl_file` (str or Path only)"
            raise TypeError(msg)
        try:
            with Path(curl_file).open(encoding="utf-8") as fs:
                return cls(fs.readlines())
        except FileNotFoundError as exc:
            msg = "Incorrect file name or Path object"
            raise FileNotFoundError(msg) from exc

    @classmethod
    def read_from_clipboard(cls) -> Self:
        clipboard_content = pyperclip.paste()
        return cls(clipboard_content.split("\n"))

    def _fix_cmd_break_lines(self, content_with_cr: list) -> list:
        """Fix cmd windows break line, remove CR character.

        Args:
        ----
            content_with_cr (list): content containing cmd break line

        Returns:
        -------
            list: content not containing cmd break line
        """
        return [line.replace("^", "") for line in content_with_cr]

    def _parse_authdata(self) -> None:
        """Parse content of curl file to AuthData(headers, data, params) dataclass.

        Args:
        ----
            content (list[str]): content of file 'copy as cURL' from browser

        Returns:
        -------
            AuthData: dataclass for store data for authentification on Youtube Music
        """
        # Parsing 'params' section
        post_url = shlex.split(self.raw_curl_content[0])[1]
        query_post_url = urlsplit(post_url).query
        post_params = dict(parse_qsl(query_post_url))
        # Parsing 'data' section
        raw_data = shlex.split(s=self.raw_curl_content[-2])[1]
        json_data = json.loads(s=raw_data)
        # delete default browse id
        json_data.pop("browseId", None)
        # Parsing 'headers' section
        raw_headers = self.raw_curl_content[1:-2]
        # Parse str  "-H 'key: value' \\\n" to "key: value"
        raw_headers_list = [shlex.split(raw_line)[1] for raw_line in raw_headers]
        # Parse "key: value" to [key, value] and filter list if lenght <2 (lost value)
        # Split method run twice, but that most clearly, than walrus operator in list comprehansion
        headers_list = [line.split(": ") for line in raw_headers_list if len(line.split(": ")) == 2]
        headers = dict(headers_list)
        self.headers = headers
        self.params = post_params
        self.json_data = json_data


def search_authfiles_in_dir(dir_path: str | Path) -> dict[str, AuthData]:
    """Scan dir to authdata files.

    Args:
    ----
        dir_path (str | Path): path to curl files

    Returns:
    -------
        dict[str, AuthData]: {filename: AuthData}
    """
    auth_files: dict = {}
    if isinstance(dir_path, str) and "\\" in dir_path:
        dir_path = dir_path.replace("\\", "/")
    dir_path = Path(dir_path)
    if Path(dir_path).is_dir():
        files = dir_path.glob("*")
        for file in files:
            try:
                auth_files |= {file.name: AuthData.read_from_file(curl_file=file)}
            except ParsingError:
                continue
    return auth_files


def dump_authdata(authdata: AuthData, filename: str, authfiles_dir: str | Path = "files/auth/") -> None:
    """Dump from curl data to file.

    Args:
    ----
        authdata (AuthData): AuthData instance
        filename (str): name of the saved file
        authfiles_dir (str | Path, optional): Dir for saved files. Defaults to "files/auth/".

    Raises:
    ------
        DumpAuthFileError: Raw curl content not found in instance.
    """
    if authdata.raw_curl_content:
        with Path(f"{authfiles_dir}/{filename}").open(mode="w", encoding="utf-8") as fs:
            fs.write("".join(authdata.raw_curl_content))
    else:
        msg = "Raw curl content not found."
        raise DumpAuthFileError(msg)
