"""Application errors."""


class AppError(Exception):
    """Base class for errors raised by this app."""


class ValidationError(AppError):
    """Bad input."""


class NotFoundError(AppError):
    """Missing record."""


class InsufficientFunds(AppError):
    """Balance too low."""
