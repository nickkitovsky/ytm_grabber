"""Exceptions module."""


class TooManyRetryError(Exception):
    """TooManyRetryError exception class for retry decorator."""


class ExistingClientNotFoundError(Exception):
    """Api client not found."""


class PayloadError(Exception):
    """Wrong payload format."""


class AuthFilesError(Exception):
    """Parse authfile error."""


class AuthDataError(Exception):
    """Error loading authdata."""


class DumpAuthFileError(Exception):
    """Curl file content not found."""


class ParsingError(Exception):
    """Error of parsing data."""
