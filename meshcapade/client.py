"""
Base client for MeshCapade API requests
"""
import requests
from .exceptions import APIError, AuthenticationError, ResourceNotFoundError

class BaseClient:
    """Base client for making requests to the MeshCapade API"""
    
    def __init__(self, api_key=None, api_url=None):
        from meshcapade import API_URL, API_KEY
        self.api_url = api_url or API_URL
        self.api_key = api_key or API_KEY
        
        if not self.api_key:
            raise AuthenticationError("API key is not set. Please use meshcapade.set_api_key() to set your API key.")
            
    def make_request(self, method, endpoint, data=None, headers=None, files=None, params=None):
        """Make a request to the MeshCapade API.
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint (str): API endpoint to call
            data (dict, optional): JSON data to include in the request body
            headers (dict, optional): Additional headers to include in the request
            files (dict, optional): Files to upload
            params (dict, optional): URL parameters
            
        Returns:
            dict: The JSON response from the API
            
        Raises:
            APIError: If the request fails
            AuthenticationError: If authentication fails
            ResourceNotFoundError: If the requested resource is not found
        """
        # Default headers
        default_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Merge default headers with any additional headers
        if headers:
            default_headers.update(headers)
            
        # If we're sending files, remove Content-Type as it will be set automatically
        if files:
            default_headers.pop("Content-Type", None)
        
        # Construct the full URL
        url = f"{self.api_url}/{endpoint}"
        
        # Debug print the request details
        print(f"Making {method} request to {url}")
        if data:
            print(f"Request data: {data}")
        if params:
            print(f"Request params: {params}")
        
        # Make the request
        try:
            response = requests.request(
                method=method, 
                url=url, 
                headers=default_headers, 
                json=data if data and not files else None,
                data=data if files and data else None,
                files=files,
                params=params
            )
            
            # Print the response status
            print(f"Response status: {response.status_code}")
            
            # Handle different status codes
            if response.status_code == 401:
                raise AuthenticationError("Authentication failed. Please check your API key.")
            
            if response.status_code == 404:
                raise ResourceNotFoundError(f"Resource not found: {url}")
            
            # Raise an exception for 4XX/5XX status codes
            if response.status_code >= 400:
                error_msg = f"{response.status_code} {response.reason} for url: {url}"
                try:
                    error_json = response.json()
                    if "error" in error_json:
                        error_msg = f"{error_msg}\nAPI Error: {error_json['error']}"
                    print(f"Error response: {error_json}")
                except:
                    print(f"Error response text: {response.text}")
                    pass
                raise APIError(f"API request failed: {error_msg}", status_code=response.status_code)
            
            # Parse and return JSON response if available
            if response.headers.get('Content-Type', '').startswith('application/json') or response.headers.get('Content-Type', '').startswith('application/vnd.api+json'):
                return response.json()
            else:
                # For non-JSON responses, return a dict with status and raw content
                return {
                    "status_code": response.status_code,
                    "content": response.content,
                    "headers": dict(response.headers)
                }
                
        except requests.exceptions.HTTPError as e:
            # Try to parse error response as JSON
            try:
                error_json = response.json()
                raise APIError(
                    message=f"API request failed: {error_json.get('message', str(e))}",
                    status_code=response.status_code,
                    response=error_json
                )
            except ValueError:
                # If error isn't JSON, just raise the original error
                raise APIError(f"API request failed: {str(e)}", status_code=response.status_code)
                
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")