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


class HandlerError(Exception):
    """Base exception for all handler errors."""

    pass


class TripNotFoundError(HandlerError):
    """Exception raised when a trip is not found."""

    def __init__(self, trip_id: str):
        self.trip_id = trip_id
        super().__init__(f"Trip with id {trip_id} not found.")


class TripAlreadyExistsError(HandlerError):
    """Exception raised when trying to create a trip that already exists."""

    def __init__(self, trip_id: str):
        self.trip_id = trip_id
        super().__init__(f"Trip with id {trip_id} already exists.")


class InvalidTripDataError(HandlerError):
    """Exception raised when trip data is invalid."""

    def __init__(self, details: str):
        self.details = details
        super().__init__(f"Invalid trip data: {details}")
