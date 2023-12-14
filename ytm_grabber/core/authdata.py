"""Module for working with auth files."""
import json
import shlex
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

import pyperclip  # type: ignore[import-untyped]

from ytm_grabber.core.custom_exceptions import ParsingError


@dataclass
class AuthData:
    """Data for authentification on Youtube Music."""

    headers: dict
    params: dict
    json_data: dict


def get_authdata(raw_curl_data: str | Path | list[str]) -> AuthData | None:
    """Load session data from curl file.

    Args:
    ----
        raw_curl_data (str | Path | list[str]):  Path to curl file

    Returns:
    -------
        AuthData: dataclass for store data for authentification on Youtube Music
    """
    curl_contents = (
        _read_from_file(curl_file=raw_curl_data) if isinstance(raw_curl_data, (str, Path)) else raw_curl_data
    )
    try:
        return parse_content(curl_contents)
    except IndexError as exc:
        msg = "error of parse curl_data"
        raise ParsingError(msg) from exc


def get_authdata_from_dir(dir_path: str | Path) -> dict[str, AuthData]:
    """Load AuthData from dir.

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
                auth_files |= {file.name: get_authdata(raw_curl_data=file)}
            except ParsingError:
                continue
    return auth_files


def _read_from_file(curl_file: str | Path) -> list[str]:
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
        list[str]: Content of 'curl file'
    """
    if not isinstance(curl_file, (str, Path)):
        msg = "Incorrect type of `curl_file` (str or Path only)"
        raise TypeError(msg)
    try:
        with open(curl_file, encoding="utf-8") as fs:
            return fs.readlines()
    except FileNotFoundError as exc:
        msg = "Incorrect file name or Path object"
        raise FileNotFoundError(msg) from exc


def _read_from_clipboard() -> list[str]:
    clipboard_content = pyperclip.paste()
    if "^" in clipboard_content:  # if select copy as cURL (cmd)
        # normalize windows (cmd) endline symbols
        clipboard_content = clipboard_content.replace("^", "").split("\r\n")
    else:  # if select copy as cURL (bash)
        # normalize bash endline symbols (from clipboard)
        clipboard_content = clipboard_content.replace("\\\r\n", "\\\n").split("\\\n")
    return clipboard_content


def parse_content(content: list[str]) -> AuthData:
    """Parse content of curl file to AuthData(headers, data, params) dataclass.

    Args:
    ----
        content (list[str]): content of file 'copy as cURL' from browser

    Returns:
    -------
        AuthData: dataclass for store data for authentification on Youtube Music
    """
    # Parsing 'params' section
    post_url = shlex.split(content[0])[1]
    query_post_url = urlsplit(post_url).query
    post_params = dict(parse_qsl(query_post_url))
    # Parsing 'data' section
    raw_data = shlex.split(s=content[-2])[1]
    json_data = json.loads(s=raw_data)
    # delete default browse id
    json_data.pop("browseId", None)
    # Parsing 'headers' section
    raw_headers = content[1:-2]
    # Parse str  "-H 'key: value' \\\n" to "key: value"
    raw_headers_list = [shlex.split(raw_line)[1] for raw_line in raw_headers]
    # Parse "key: value" to [key, value] and filter list if lenght <2 (lost value)
    # Split method run twice, but that most clearly, than walrus operator in list comprehansion
    headers_list = [line.split(": ") for line in raw_headers_list if len(line.split(": ")) == 2]
    headers = dict(headers_list)

    return AuthData(headers=headers, json_data=json_data, params=post_params)
