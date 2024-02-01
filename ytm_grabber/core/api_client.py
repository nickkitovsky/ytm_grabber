"""API client YoutubeMusic."""


import atexit
from typing import Self

import httpx

from ytm_grabber.core.authdata import AuthData
from ytm_grabber.core.custom_exceptions import AuthDataError, ExistingClientNotFoundError


class ApiClient:
    """Client for YoutubeMusic API (class uses Singleton pattern).

    Recomended: ApiClient.create_client(AuthData) function.
    Alternative: create ApiClient() object and then use load_auth_data(AuthData) function.
    """

    UNAUTHORIZED_CODE = 401
    OK_CODE = 200
    # store class instance for use singleton pattern
    _instance = None

    def __new__(cls, *args, **kwargs) -> Self:
        """Overview __new__ method, for use single instance of object (singleton pattern).

        Args:
        ----
            args: Any positional arguments.
            kwargs: Any keywords arguments.

        Returns:
        -------
            Self: new instance or exist instance of client.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    def setup_client(self, auth_data: AuthData) -> None:
        """Initialize client for YoutubeMusic API.

        Args:
        ----
            auth_data (AuthData): data from parsed curl file
        """
        self.auth_data = auth_data
        self.client = self._init_client()
        atexit.register(self._close_client, self.client)

    @classmethod
    def create_client(cls, authdata: AuthData) -> Self:
        """Classmethod for create client.

        Args:
        ----
            authdata (AuthData): data from parsed curl file

        Returns:
        -------
            Self: new instance or exist instance of client.
        """
        api_client = cls()
        api_client.setup_client(auth_data=authdata)
        return api_client

    @classmethod
    def get_exist_client(cls) -> Self | None:
        """Classmethod for get exist client.

        Raises
        ------
            ExistingClientNotFoundError: instance of ApiClient not found

        Returns
        -------
            instance: exist instance of client.
        """
        if hasattr(cls._instance, "client"):
            return cls()
        msg = "Instance not found. First use ApiClient.create_client(AuthData) function."
        raise ExistingClientNotFoundError(msg)

    # @retry(5, 1)
    def send_request(self, payload: dict, url: str, timeout: int = 10) -> dict | None:
        """Send request to API.

        Args:
        ----
            payload (dict): request API payload
            url (str): url to send request.
            timeout (int): timeout for request (default 10)

        Raises:
        ------
            httpx.ResponseNotRead: _description_

        Returns:
        -------
            dict | None: _description_
        """
        json_data_with_payload = self.auth_data.json_data | payload
        response = self.client.post(
            url=url,
            timeout=timeout,
            headers=self.auth_data.headers,
            params=self.auth_data.params,
            json=json_data_with_payload,
        )
        match response:
            case httpx.Response() if response.status_code == self.OK_CODE:
                return response.json()
            case httpx.Response() if response.status_code == self.UNAUTHORIZED_CODE:
                msg = "Auth data is not valid. Please update auth data."
                raise AuthDataError(msg)
            case _:
                raise httpx.ResponseNotRead

    def _init_client(self) -> httpx.Client:
        return httpx.Client()

    def _close_client(self, client: httpx.Client) -> None:
        client.close()
