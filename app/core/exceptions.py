class AppException(Exception):
    """Base application exception."""


class AuthenticationError(AppException):
    """Raised when authentication fails."""


class AuthorizationError(AppException):
    """Raised when authorization fails."""


class UserAlreadyExistsError(AppException):
    """Raised when a user already exists."""


class InvalidCredentialsError(AppException):
    """Raised when email/password is invalid."""


class InactiveUserError(AppException):
    """Raised when a user is inactive."""


class UserNotFoundError(AppException):
    """Raised when a user cannot be found."""