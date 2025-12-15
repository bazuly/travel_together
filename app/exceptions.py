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
