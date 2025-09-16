"""Company domain specific exceptions."""


class CompanyNotFoundError(Exception):
    """Exception raised when company is not found."""
    pass


class CompanyAlreadyExistsError(Exception):
    """Exception raised when trying to create a company that already exists."""
    pass


class CompanyValidationError(Exception):
    """Exception raised when company data validation fails."""
    pass


class CompanyDeletionError(Exception):
    """Exception raised when company cannot be deleted."""
    pass