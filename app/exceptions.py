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
# USER LAYER EXCEPTIONS
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
# TRIP LAYER EXCEPTIONS
# =============================================================================


class TripRepositoryError(Exception):
    """Base exception for all service layer errors."""

    pass


class TripNotFoundError(TripRepositoryError):
    """Exception raised when a trip is not found in service layer."""

    def __init__(self, trip_id: uuid.UUID):
        self.trip_id = trip_id
        super().__init__(f"Trip with id {trip_id} not found.")


class TripOrganizerRequiredError(Exception):
    """Organizer required exception"""

    pass


class AlreadyTripParticipant(Exception):
    """Exception raise when the user already participant"""

    pass


class ReachedMaxParticipants(Exception):
    """Exception raise if reached maximum amount of participants"""

    pass


# =============================================================================
# PARTICIPANT LAYER EXCEPTIONS
# =============================================================================


class ParticipantNotFoundError(Exception):
    """Exception raised when a participant is not found in service layer."""

    def __init__(self, participant_id: uuid.UUID, trip_id: uuid.UUID):
        self.participant_id = participant_id
        self.trip_id = trip_id
        super().__init__(
            f"Participant with id {participant_id} not found in trip {trip_id}."
        )


class ParticipantNotActiveError(Exception):
    """Exception raised when participant status is not active."""

    def __init__(self, participant_id: uuid.UUID):
        self.participant_id = participant_id
        super().__init__(f"Participant with id {participant_id} is not active.")


class MaximumAmountOfParticipantsError(Exception):
    """Exception raised when participant status is not active."""

    def __init__(self, trip_id: uuid.UUID):
        self.trip_id = trip_id
        super().__init__(f"Trip with id {trip_id} has maximum amount of participants.")


class AllParticipantFromTripError(Exception):
    """Exception raise when unable to fetch all members from trip"""

    pass


# =============================================================================
# EXPENSE LAYER EXCEPTIONS
# =============================================================================


class ExpenseRepositoryError(Exception):
    """Base exception for all service layer errors."""

    pass


class ExpenseNotFoundError(ExpenseRepositoryError):
    """Exception raised when a trip is not found in service layer."""

    def __init__(self, expense_id: uuid.UUID):
        self.expense_id = expense_id
        super().__init__(f"Expense with id {expense_id} not found.")


class ExpensePayerRequiredError(Exception):
    """Expense payer required exception"""

    def __init__(self, expense_id: uuid.UUID):
        self.expense_id = expense_id
        super().__init__(
            f"Only the expense creator can update or delete expense_data! Expense_id: {expense_id}"
        )
