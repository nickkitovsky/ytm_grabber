"""Exceptions module."""


class PayloadError(Exception):
    """Wrong payload format."""


class AuthFilesError(Exception):
    """Parse authfile error."""


class AuthDataError(Exception):
    """Error loading authdata."""
