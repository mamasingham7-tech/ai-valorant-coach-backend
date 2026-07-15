class DomainException(Exception):
    """Base class for all domain-related exceptions."""
    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code

class EntityNotFoundException(DomainException):
    """Exception raised when a requested resource is not found."""
    def __init__(self, message: str, code: str = "NOT_FOUND"):
        super().__init__(message, code)

class ValidationException(DomainException):
    """Exception raised when input data fails domain verification checks."""
    def __init__(self, message: str, code: str = "VALIDATION_ERROR", errors: dict = None):
        super().__init__(message, code)
        self.errors = errors

class AuthenticationException(DomainException):
    """Exception raised during login, credential check, or token verification."""
    def __init__(self, message: str, code: str = "UNAUTHENTICATED"):
        super().__init__(message, code)

class AuthorizationException(DomainException):
    """Exception raised when a user does not have permission to access a resource."""
    def __init__(self, message: str, code: str = "UNAUTHORIZED"):
        super().__init__(message, code)

class TokenExpiredException(AuthenticationException):
    """Exception raised when a token is expired."""
    def __init__(self, message: str = "Token has expired", code: str = "TOKEN_EXPIRED"):
        super().__init__(message, code)

class TokenRevokedException(AuthenticationException):
    """Exception raised when a token has been explicitly blacklisted or revoked."""
    def __init__(self, message: str = "Token has been revoked", code: str = "TOKEN_REVOKED"):
        super().__init__(message, code)
