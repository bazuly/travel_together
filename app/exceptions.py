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

    def __init__(self, message: str = "Repository error"):
        super().__init__(message)
