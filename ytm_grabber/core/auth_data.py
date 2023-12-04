"""Module for working with auth files."""
import json
import shlex
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

from ytm_grabber.core.custom_exceptions import ParsingError


@dataclass
class AuthData:
    """Data for authentification on Youtube Music."""

    headers: dict
    params: dict
    json_data: dict


def load_auth_data(curl_file: str | Path) -> AuthData | None:
    """Load session data from curl file.

    Args:
        curl_file (str | Path):  Path to curl file

    Returns:
        AuthData: dataclass for store data for authentification on Youtube Music
    """
    curl_file_contents = _read_curl_file(curl_file=curl_file)
    try:
        return _parse_curl_file(curl_file_contents)
    except IndexError:
        raise ParsingError(f'error of parse {curl_file}')


def load_authdata_from_dir(dir_path: str | Path) -> dict[str, AuthData]:
    """Load AuthData from dir.

    Args:
        dir_path (str | Path): path to curl files

    Returns:
        dict[str, AuthData]: {filename: AuthData}
    """
    auth_files = {}
    if isinstance(dir_path, str) and '\\' in dir_path:
        dir_path = dir_path.replace('\\', '/')
    dir_path = Path(dir_path)
    if Path(dir_path).is_dir():
        files = dir_path.glob('*')
        for file in files:
            try:
                auth_files |= {file.name: load_auth_data(curl_file=file)}
            except ParsingError:
                continue
    return auth_files


def _read_curl_file(curl_file: str | Path) -> list[str]:
    """Read file from browser, with your session from Dev tools, and then 'copy as cURL'.

    Args:
        curl_file (str | Path): Path to file

    Raises:
        TypeError: Wrong type. You must pass str or Path object
        FileNotFoundError: Wrong file path

    Returns:
        list[str]: Content of 'curl file'
    """
    if not isinstance(curl_file, (str, Path)):
        raise TypeError('Incorrect type of `curl_file` (str or Path only)')
    try:
        with open(curl_file, 'r', encoding='utf-8') as fs:
            return fs.readlines()
    except FileNotFoundError:
        raise FileNotFoundError('Incorrect file name or Path object')


def _parse_curl_file(curl_file_content: list[str]) -> AuthData:
    """Parse content of curl file to AuthData(headers, data, params) dataclass.

    Args:
        curl_file_content (list[str]): content of file 'copy as cURL' from browser

    Returns:
        AuthData: dataclass for store data for authentification on Youtube Music
    """
    # Parsing 'params' section
    post_url = shlex.split(curl_file_content[0])[1]
    query_post_url = urlsplit(post_url).query
    post_params = dict(parse_qsl(query_post_url))
    # Parsing 'data' section
    raw_data = shlex.split(s=curl_file_content[-2])[1]
    json_data = json.loads(s=raw_data)
    # delete default browse id
    json_data.pop('browseId', None)
    # Parsing 'headers' section
    raw_headers = curl_file_content[1:-2]
    # Parse str  "-H 'key: value' \\\n" to "key: value"
    raw_headers_list = [shlex.split(raw_line)[1] for raw_line in raw_headers]
    # Parse "key: value" to [key, value] and filter list if lenght <2 (lost value)
    # FIXME: split method run twice, but that most clearly, than walrus operator in list comprehansion
    # FIXME: Jones Complexity 17.
    headers_list = [line.split(': ') for line in raw_headers_list if len(line.split(': ')) == 2]
    headers = dict(headers_list)

    return AuthData(headers=headers, json_data=json_data, params=post_params)
