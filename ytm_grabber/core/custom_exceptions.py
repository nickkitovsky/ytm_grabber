"""Exceptions module."""


class TooManyRetryError(Exception):
    """TooManyRetryError exception class for retry decorator."""


class PayloadError(Exception):
    """Wrong payload format."""


class AuthFilesError(Exception):
    """Parse authfile error."""


class AuthDataError(Exception):
    """Error loading authdata."""
