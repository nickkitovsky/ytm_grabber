"""Exceptions module."""


class TooManyRetryError(Exception):
    """TooManyRetryError exception class for retry decorator."""


class ParsingError(Exception):
    """Error of parsing data."""


class PayloadError(Exception):
    """Wrong payload format."""


class AuthFilesError(Exception):
    """Parse authfile error."""


class AuthDataError(Exception):
    """Error loading authdata."""


class DumpAuthFileError(Exception):
    """Curl file content not found."""
