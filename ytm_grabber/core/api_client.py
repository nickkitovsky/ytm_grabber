"""API client YoutubeMusic."""


import atexit
import functools
import time
from typing import Self

import httpx

from ytm_grabber.core.authdata import AuthData


class TooManyRetryError(Exception):
    """TooManyRetryError exception class for retry decorator."""


class ExistingClientNotFoundError(Exception):
    """TooManyRetryError exception class for retry decorator."""


def retry(attempts_number: int, retry_sleep_sec: int):
    """Retry attempts run of function.

    Args:
    ----
        attempts_number (int): number of attempts
        retry_sleep_sec (int): sleep between attempts

    Returns:
    -------
        none: this is decorator
    """

    def decarator(func):
        @functools.wraps(wrapped=func)
        def wrapper(*args, **kwargs):
            # TODO: For logging change '_' to attempt
            for _ in range(attempts_number):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    time.sleep(retry_sleep_sec)
                # TODO: Add logging 'Trying attempt {attempt+1} of {attempts_number}'

            # TODO: Add logging 'func {func.__name__} retry failed'
            msg = f"Exceed max retry num: {attempts_number} failed."
            raise TooManyRetryError(
                msg,
            )

        return wrapper

    return decarator


class ApiClient:
    """Client for YoutubeMusic API (class uses Singleton pattern).

    Recomended: ApiClient.create_client(AuthData) function.
    Alternative: create ApiClient() object and then use load_auth_data(AuthData) function.
    """

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
        msg = "Instance not found. First use ApiClient.create_clinet(AuthData) function."
        raise ExistingClientNotFoundError(msg)

    @retry(5, 1)
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
        if response.is_success:
            return response.json()
        # TODO: Add logging 'Error of get response with:\n%s', payload
        raise httpx.ResponseNotRead

    def _init_client(self) -> httpx.Client:
        return httpx.Client()

    def _close_client(self, client: httpx.Client) -> None:
        client.close()
