"""
MeshCapade SDK - A Python client for interacting with the MeshCapade API
"""

# SDK version
__version__ = "0.1.0"

# Base API URL for all requests
API_URL = "https://api.meshcapade.com/api/v1"

# API Key for authentication
API_KEY = None

def set_api_key(api_key: str):
    """Set the API key for authentication with Meshcapade API
    
    Args:
        api_key (str): The API key provided by Meshcapade
    """
    global API_KEY
    API_KEY = api_key

def set_api_url(api_url: str):
    """Set a custom API URL for the Meshcapade API
    
    This is primarily used for testing or if Meshcapade provides a different API endpoint.
    
    Args:
        api_url (str): The custom API URL
    """
    global API_URL
    API_URL = api_url

# Import exceptions for easier access
from .exceptions import (
    MeshCapadeError,
    AuthenticationError, 
    APIError,
    ValidationError,
    ResourceNotFoundError,
    TimeoutError
)

# Import main components
from .avatar import Avatar
from .client import BaseClient

# For convenient imports
__all__ = [
    'Avatar',
    'BaseClient',
    'set_api_key',
    'set_api_url',
    'MeshCapadeError',
    'AuthenticationError',
    'APIError',
    'ValidationError',
    'ResourceNotFoundError',
    'TimeoutError'
]