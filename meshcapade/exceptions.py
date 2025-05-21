"""
Custom exceptions for the MeshCapade SDK
"""

class MeshCapadeError(Exception):
    """Base exception for all MeshCapade SDK errors"""
    pass

class AuthenticationError(MeshCapadeError):
    """Exception raised for authentication issues"""
    pass

class APIError(MeshCapadeError):
    """Exception raised for API errors"""
    def __init__(self, message, status_code=None, response=None):
        self.status_code = status_code
        self.response = response
        super().__init__(message)

class ValidationError(MeshCapadeError):
    """Exception raised for validation errors"""
    pass

class ResourceNotFoundError(MeshCapadeError):
    """Exception raised when a resource is not found"""
    pass

class TimeoutError(MeshCapadeError):
    """Exception raised when an operation times out"""
    pass