import uuid


# =============================================================================
# DATABASE LAYER EXCEPTIONS
# =============================================================================


class DatabaseError(Exception):
    """Base exception for all database errors."""

    pass


class DatabaseConnectionError(DatabaseError):
    """Exception raised when a database connection cannot be established."""

    def __init__(self, details: str):
        self.details = details
        message = "Failed to connect to database."
        if details:
            message += f" Details: {details}"
        super().__init__(message)


class RepositoryError(DatabaseError):
    """Default repository exception."""

    def __init__(
        self, message: str = "Repository error, failed to commit transaction."
    ):
        super().__init__(message)


# =============================================================================
# USER REPOSITORY LAYER EXCEPTIONS
# =============================================================================


class UserRepositoryError(Exception):
    """Base exception for all service layer errors."""

    pass


class UserNotFoundError(UserRepositoryError):
    """Exception raised when a user is not found in service layer."""

    def __init__(self, user_data: str | uuid.UUID):
        self.user_data = user_data
        if isinstance(user_data, str):
            super().__init__(f"User with email {user_data} not found.")
        else:
            super().__init__(f"User with id {user_data} not found.")


class UserNotFoundExceptionAuth(Exception):
    """Exception raised when a user is not found in auth layer."""

    def __init__(self):
        super().__init__("Can not authenticated user")


class UserIncorrectPasswordException(Exception):
    """Exception raised when a user is not found in auth layer."""

    def __init__(self, user):
        self.user = user.email
        super().__init__(f"Incorrect password for user {user.email}.")


# =============================================================================
# TRIP REPOSITORY LAYER EXCEPTIONS
# =============================================================================


class TripRepositoryError(Exception):
    """Base exception for all service layer errors."""

    pass


class TripNotFoundError(TripRepositoryError):
    """Exception raised when a trip is not found in service layer."""

    def __init__(self, trip_id: uuid.UUID):
        self.trip_id = trip_id
        super().__init__(f"Trip with id {trip_id} not found.")
