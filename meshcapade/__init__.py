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

# Import main components for easier access
from .avatar import Avatar