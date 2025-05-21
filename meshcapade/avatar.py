class Avatar:
    def __init__(self):
        self.name = None
        self.height = None
        self.weight = None
        self.gender = None
        self.avatar_id = None
        # Import API_URL and API_KEY from the package's __init__.py
        from meshcapade import API_URL, API_KEY
        self.avatars_endpoint = f"{API_URL}/avatars"
        self.api_key = API_KEY
        
        if not self.api_key:
            raise ValueError("API key is not set. Please use meshcapade.set_api_key() to set your API key.")
    
    def set_name(self, name: str):
        """Set the avatar name"""
        self.name = name
        return self
        
    def set_height(self, height: int):
        """Set the avatar height in cm"""
        self.height = height
        return self
        
    def set_weight(self, weight: int):
        """Set the avatar weight in kg"""
        self.weight = weight
        return self
        
    def set_gender(self, gender: str):
        """Set the avatar gender (male/female)"""
        self.gender = gender
        return self
    
    def _make_request(self, method: str, endpoint: str, data: dict = None, headers: dict = None, files=None, params=None):
        """Make a request to the MeshCapade API.
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint (str): API endpoint to call, will be appended to the avatars_endpoint base URL
            data (dict, optional): JSON data to include in the request body. Defaults to None.
            headers (dict, optional): Additional headers to include in the request. Defaults to None.
            files (dict, optional): Files to upload. Defaults to None.
            params (dict, optional): URL parameters. Defaults to None.
            
        Returns:
            dict: The JSON response from the API
            
        Raises:
            Exception: If the request fails
        """
        import requests
        
        # Default headers
        default_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Merge default headers with any additional headers
        if headers:
            default_headers.update(headers)
        
        # Construct the full URL
        url = f"{self.avatars_endpoint}/{endpoint}"
        
        # Print request details for debugging
        print(f"Making {method} request to {url}")
        if data:
            print(f"Request data: {data}")
        
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
            
            print(f"Response status code: {response.status_code}")
            
            # Raise an exception for 4XX/5XX status codes
            response.raise_for_status()
            
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
            print(f"HTTP Error: {e}")
            # Try to parse error response as JSON
            try:
                error_json = response.json()
                print(f"Error response: {error_json}")
                raise Exception(f"API request failed: {error_json.get('message', str(e))}")
            except ValueError:
                # If error isn't JSON, just raise the original error
                raise Exception(f"API request failed: {str(e)}")
                
        except requests.exceptions.RequestException as e:
            print(f"Request Exception: {e}")
            raise Exception(f"API request failed: {str(e)}")
    def create_avatar_from_image(self, image_paths=None):
        """Create a new avatar through the complete creation process.
        
        This is a high-level method that orchestrates the complete avatar creation process:
        1. Creates an empty avatar entry in the system
        2. Uploads user images for the avatar
        3. Initiates the avatar generation process from those images
        4. Returns the created avatar data
        
        Args:
            image_paths (list, optional): List of file paths to images to upload.
                                         Default is None.
        
        Returns:
            str: The created avatar ID
        
        Raises:
            ValueError: If required properties (name, height, weight, gender) are not set
        """
        # Check if required properties are set
        if self.name is None or self.height is None or self.weight is None or self.gender is None:
            raise ValueError("Required properties (name, height, weight, gender) must be set before creating an avatar. "
                            "Use set_name(), set_height(), set_weight(), and set_gender() methods.")
            
        print(f"Creating avatar with name: {self.name}, height: {self.height}, weight: {self.weight}, gender: {self.gender}")
        
        # Step 1: Create an empty avatar
        avatar_data = self._create_empty_avatar()
        
        # Validate avatar_data and extract ID
        if not avatar_data or 'id' not in avatar_data:
            raise ValueError("Failed to get avatar ID from API response.")
        
        # Store the avatar ID
        self.avatar_id = avatar_data['id']
        print(f"Created empty avatar with ID: {self.avatar_id}")
        
        # Step 2: Upload images for the avatar
        print(f"Uploading images for avatar ID: {self.avatar_id}")
        self._upload_images(self.avatar_id, image_paths)
        print(f"Images uploaded for avatar ID: {self.avatar_id}")
        
        # Step 3: Start the fitting process using the uploaded images
        self._start_fitting_process(self.avatar_id)
        print(f"Fitting process started for avatar ID: {self.avatar_id}")

        # Step 4: Get the finalized avatar data
        # final_avatar = self._get_processed_avatar(avatar_data['id'])
        
        return self.avatar_id
    
    def _create_empty_avatar(self):
        """Create an empty avatar entry in the system.
        
        Returns:
            dict: The initial avatar data including the avatar ID
        """
        response = self._make_request("POST", "create/from-images")
        print(f"Create empty avatar response: {response}")
        
        
        if "data" in response and "id" in response["data"]:
            # Store avatar ID as an instance attribute for future operations
            self.id = response["data"]["id"]
                
            # Return the full response data for further processing
            return response["data"]
            
        
                    
        # If we get here, we couldn't extract the avatar ID
        raise ValueError("Failed to create avatar: Invalid API response")
    
    def _upload_images(self, avatar_id, image_paths=None):
        """Upload images for avatar creation.
        
        Args:
            avatar_id (str): The ID of the avatar to upload images for
            image_paths (list): List of file paths to images to upload
        
        Returns:
            dict: Response data from the image upload process
        """
        if not image_paths:
            print("No images provided for upload. Using default test images.")
            # For demonstration purposes, assume we have default test images
            # In a real implementation, this should raise an error if no images are provided
            return {"status": "skipped", "message": "No images provided"}
        
        import os
        
        upload_results = []
        for image_path in image_paths:
            if not os.path.exists(image_path):
                print(f"Image file not found: {image_path}")
                continue
                
            # STEP 1: Request a pre-signed URL for S3 upload
            presigned_data = self._make_request("POST", f"{avatar_id}/images")
            print(f"Presigned URL response: {presigned_data}")
            
            # Check if we received a valid response with an upload URL
            if ("data" not in presigned_data or 
                "links" not in presigned_data["data"] or 
                "upload" not in presigned_data["data"]["links"]):
                upload_results.append({
                    "status": "failed", 
                    "message": "Failed to get upload URL", 
                    "file": os.path.basename(image_path)
                })
                continue
            
            # Extract the S3 upload URL
            upload_url = presigned_data["data"]["links"]["upload"]
            image_id = presigned_data["data"]["id"]
            
            # STEP 2: Upload the actual image to the pre-signed S3 URL
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                
                # S3 PUT request doesn't need authentication headers - the URL is pre-signed
                s3_headers = {
                    'Content-Type': 'image/jpeg'  # Adjust based on actual image type if needed
                }
                
                import requests
                s3_response = requests.put(upload_url, headers=s3_headers, data=image_data)
                print(f"S3 upload response: {s3_response.status_code}")
                if s3_response.status_code == 200:
                    upload_results.append({
                        "status": "success", 
                        "message": "Image uploaded successfully",
                        "image_id": image_id,
                        "avatar_id": avatar_id,
                        "file": os.path.basename(image_path)
                    })
                else:
                    upload_results.append({
                        "status": "failed", 
                        "message": f"S3 upload failed with status code: {s3_response.status_code}",
                        "file": os.path.basename(image_path)
                    })
        
        return {"uploaded_images": upload_results}
    
    def _start_fitting_process(self, avatar_id):
        """Start the fitting process to create an avatar from uploaded images.
        
        Args:
            avatar_id (str): The ID of the avatar to process
        
        Returns:
            dict: Response data from the fitting process initiation
        """
        # Prepare the request body with avatar details
        body = {
            "avatarname": self.name,
            "height": self.height,
            "weight": self.weight,
            "gender": self.gender
        }
        
        # Send the fit-to-images request
        return self._make_request("POST", f"{avatar_id}/fit-to-images", body)
    
    def get_avatar(self, avatar_id):
        """Get the processed avatar data after fitting is complete.
        
        Args:
            avatar_id (str): The ID of the avatar to retrieve
        
        Returns:
            dict: The final avatar data
        """
        return self._make_request("GET", f"{avatar_id}", {})
    def download_avatar(self, avatar_id=None, filename="avatar.obj", polling_interval=5):
        """Download the avatar 3D model.
        
        This method polls the API until the avatar is ready for download,
        then downloads and saves the 3D model to the specified filename.
        
        Args:
            avatar_id (str, optional): The ID of the avatar to download. 
                                      If not provided, uses the current avatar_id.
            filename (str, optional): The filename to save the avatar model to.
                                     Defaults to "avatar.obj".
            polling_interval (int, optional): How often to check if the avatar is ready, in seconds.
                                            Defaults to 5 seconds.
        
        Returns:
            str: The path to the downloaded file
        
        Raises:
            ValueError: If avatar_id is not provided and there's no current avatar_id
            Exception: If avatar processing fails
        """
        import time
        import requests
        import os
        
        # Use the provided avatar_id or fall back to the instance's avatar_id
        avatar_id = avatar_id or self.avatar_id
        if not avatar_id:
            raise ValueError("No avatar ID provided. Create an avatar first or provide an ID.")
            
        print(f"Checking avatar {avatar_id} for download...")
        
        # Function to poll the API until the avatar is ready
        def poll_until_ready():
            print("Polling for avatar readiness...")
            
            while True:
                # Get the current status of the avatar
                params = {"include": "exported_mesh"}
                response = self._make_request("GET", f"{avatar_id}", params=params)
                
                state = response.get("data", {}).get("attributes", {}).get("state", "")
                print(f"Current state: {state}")
                
                # Check if the avatar is ready for download
                if state == "READY":
                    # Look for mesh URLs in the included array
                    included = response.get("included", [])
                    
                    for item in included:
                        if item.get("type") == "asset" and item.get("attributes", {}).get("url", {}).get("path"):
                            download_url = item.get("attributes", {}).get("url", {}).get("path", "")
                            if download_url:
                                return download_url
                    
                    print("Avatar is ready but no suitable download URL was found")
                    time.sleep(polling_interval)
                elif state == "FAILED" or state == "ERROR":
                    raise Exception(f"Avatar processing failed with state: {state}")
                
                # Wait before polling again
                time.sleep(polling_interval)
       
        # Poll until the avatar is ready and get the download URL
        download_url = poll_until_ready()
        
        # Download the avatar file
        print(f"Downloading avatar from: {download_url}")
        response = requests.get(download_url)
        response.raise_for_status()
        
        # Save to file
        with open(filename, "wb") as f:
            f.write(response.content)
        
        print(f"Avatar saved to {os.path.abspath(filename)}")
        return filename
    def delete_avatar(self):
        # Logic to delete an avatar using the MeshCapade API
        pass
    def list_avatars(self):
        # Logic to list all avatars using the MeshCapade API
        pass
    def update_avatar(self):
        # Logic to update an avatar using the MeshCapade API
        pass
   
    def __repr__(self):
        return f"Avatar(id={self.id}, name={self.name})"
