class NotFoundError(Exception):
    """Raised when a MongoDB document is not found."""
    pass


class AlreadyExistsError(Exception):
    """Raised when attempting to insert a duplicate document."""
    pass


class ValidationError(Exception):
    """Raised when validation fails."""
    pass
