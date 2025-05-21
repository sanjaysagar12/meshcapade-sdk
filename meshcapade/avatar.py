"""
Avatar management module for the MeshCapade SDK
"""
import os
import time
import requests
from .client import BaseClient
from .exceptions import ValidationError, APIError, TimeoutError

class Avatar(BaseClient):
    """Class for managing avatars through the MeshCapade API"""
    
    def __init__(self, api_key=None, api_url=None):
        super().__init__(api_key, api_url)
        self.name = None
        self.height = None
        self.weight = None
        self.gender = None
        self.avatar_id = None
        self.avatars_endpoint = "avatars"
        
    def set_name(self, name: str):
        """Set the avatar name"""
        self.name = name
        return self
        
    def set_height(self, height: int):
        """Set the avatar height in cm"""
        if not isinstance(height, int) or height <= 0:
            raise ValidationError("Height must be a positive integer")
        self.height = height
        return self
        
    def set_weight(self, weight: int):
        """Set the avatar weight in kg"""
        if not isinstance(weight, int) or weight <= 0:
            raise ValidationError("Weight must be a positive integer")
        self.weight = weight
        return self
        
    def set_gender(self, gender: str):
        """Set the avatar gender (male/female)"""
        if gender not in ["male", "female"]:
            raise ValidationError("Gender must be either 'male' or 'female'")
        self.gender = gender
        return self
    
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
            ValidationError: If required properties (name, height, weight, gender) are not set
            APIError: If the API request fails
        """
        # Check if required properties are set
        if self.name is None or self.height is None or self.weight is None or self.gender is None:
            raise ValidationError("Required properties (name, height, weight, gender) must be set before creating an avatar. "
                            "Use set_name(), set_height(), set_weight(), and set_gender() methods.")
            
        print(f"Creating avatar with name: {self.name}, height: {self.height}, weight: {self.weight}, gender: {self.gender}")
        
        # Prepare the body with required avatar metadata
        body = {
            "avatarname": self.name,
            "height": self.height,
            "weight": self.weight,
            "gender": self.gender
        }
        
        # Step 1: Create an empty avatar
        avatar_data = self._create_empty_avatar(body)
        
        # Validate avatar_data and extract ID
        if not avatar_data or 'id' not in avatar_data:
            raise APIError("Failed to get avatar ID from API response.")
        
        # Store the avatar ID
        self.avatar_id = avatar_data['id']
        print(f"Created empty avatar with ID: {self.avatar_id}")
        
        # Step 2: Upload images for the avatar
        if image_paths:
            print(f"Uploading images for avatar ID: {self.avatar_id}")
            self._upload_images(self.avatar_id, image_paths)
            print(f"Images uploaded for avatar ID: {self.avatar_id}")
        
            # Step 3: Start the fitting process using the uploaded images
            self._start_fitting_process(self.avatar_id)
            print(f"Fitting process started for avatar ID: {self.avatar_id}")

        # Return the avatar ID
        return self.avatar_id
    
    def _create_empty_avatar(self, body=None):
        """Create an empty avatar entry in the system.
        
        Args:
            body (dict, optional): The request body containing avatar metadata.
                                  Default is None.
        
        Returns:
            dict: The initial avatar data including the avatar ID
        """
        # If body is not provided, use the instance attributes
        if body is None:
            body = {
                "avatarname": self.name,
                "height": self.height,
                "weight": self.weight,
                "gender": self.gender
            }
        
        response = self.make_request("POST", f"{self.avatars_endpoint}/create/from-images", data=body)
        print(f"Create empty avatar response: {response}")
        
        if "data" in response and "id" in response["data"]:
            # Store avatar ID as an instance attribute for future operations
            self.avatar_id = response["data"]["id"]
                
            # Return the full response data for further processing
            return response["data"]
                    
        # If we get here, we couldn't extract the avatar ID
        raise APIError("Failed to create avatar: Invalid API response")
    
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
        
        upload_results = []
        for image_path in image_paths:
            if not os.path.exists(image_path):
                print(f"Image file not found: {image_path}")
                continue
                
            # STEP 1: Request a pre-signed URL for S3 upload
            presigned_data = self.make_request("POST", f"{self.avatars_endpoint}/{avatar_id}/images")
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
        return self.make_request("POST", f"{self.avatars_endpoint}/{avatar_id}/fit-to-images", body)
    
    def get_avatar(self, avatar_id=None):
        """Get the processed avatar data after fitting is complete.
        
        Args:
            avatar_id (str, optional): The ID of the avatar to retrieve.
                                      If not provided, uses the current avatar_id.
        
        Returns:
            dict: The final avatar data
        """
        avatar_id = avatar_id or self.avatar_id
        if not avatar_id:
            raise ValidationError("No avatar ID provided. Create an avatar first or provide an ID.")
            
        return self.make_request("GET", f"{self.avatars_endpoint}/{avatar_id}")
    
    def download_avatar(self, avatar_id=None, filename="avatar.obj", polling_interval=5, max_retries=60):
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
            max_retries (int, optional): Maximum number of polling attempts.
                                        Defaults to 60 (about 5 minutes with default interval).
        
        Returns:
            str: The path to the downloaded file
        
        Raises:
            ValidationError: If avatar_id is not provided and there's no current avatar_id
            TimeoutError: If avatar processing takes too long
            APIError: If avatar processing fails
        """
        import time
        import requests
        import os
        
        # Use the provided avatar_id or fall back to the instance's avatar_id
        avatar_id = avatar_id or self.avatar_id
        if not avatar_id:
            raise ValidationError("No avatar ID provided. Create an avatar first or provide an ID.")
            
        print(f"Checking avatar {avatar_id} for download...")
        
        # Function to poll the API until the avatar is ready
        retry_count = 0
        print("Polling for avatar readiness...")
        
        while retry_count < max_retries:
            # Get the current status of the avatar
            params = {"include": "exported_mesh"}
            response = self.make_request("GET", f"{self.avatars_endpoint}/{avatar_id}", params=params)
            
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
                            # Download the avatar file
                            print(f"Downloading avatar from: {download_url}")
                            response = requests.get(download_url)
                            response.raise_for_status()
                            
                            # Save to file
                            with open(filename, "wb") as f:
                                f.write(response.content)
                            
                            print(f"Avatar saved to {os.path.abspath(filename)}")
                            return filename
                
                print("Avatar is ready but no suitable download URL was found")
            elif state == "FAILED" or state == "ERROR":
                raise APIError(f"Avatar processing failed with state: {state}")
            
            # Wait before polling again
            time.sleep(polling_interval)
            retry_count += 1
        
        # If we've exhausted our retries, raise a timeout error
        raise TimeoutError(f"Avatar processing timed out after {max_retries * polling_interval} seconds")
    
    def delete_avatar(self, avatar_id=None):
        """Delete an avatar.
        
        Args:
            avatar_id (str, optional): The ID of the avatar to delete.
                                      If not provided, uses the current avatar_id.
        
        Returns:
            dict: Response data from the deletion request
        """
        avatar_id = avatar_id or self.avatar_id
        if not avatar_id:
            raise ValidationError("No avatar ID provided. Create an avatar first or provide an ID.")
            
        return self.make_request("DELETE", f"{self.avatars_endpoint}/{avatar_id}")
    
    def list_avatars(self, page=1, page_size=10):
        """List all avatars for the current API key.
        
        Args:
            page (int, optional): Page number for pagination. Defaults to 1.
            page_size (int, optional): Number of items per page. Defaults to 10.
        
        Returns:
            dict: List of avatars
        """
        params = {
            "include": "exported_mesh",
            "page": page,
            "limit": page_size
        }
        
        return self.make_request("GET", f"{self.avatars_endpoint}", params=params)
    
  
    def __repr__(self):
        return f"Avatar(id={self.avatar_id}, name={self.name})"
