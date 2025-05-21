import meshcapade
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Get API key from environment variable
api_key = os.environ.get('MESHCAPADE_API_KEY')
if not api_key:
    raise ValueError("MESHCAPADE_API_KEY environment variable is not set. Please set it before running this script.")

# Set API key
meshcapade.set_api_key(api_key)
# Define path to test images
image_folder = "/home/sagar/3d/meshcapade-sdk/test_images"
test_images = [
    os.path.join(image_folder, "women.jpg"),
]

# Create an Avatar
print("Creating a new avatar...")
avatar = meshcapade.Avatar()
avatar.set_name("hey")
avatar.set_height(165)
avatar.set_weight(85)
avatar.set_gender("female")

# Generate the avatar from images
print("Generating avatar from images...")
avatar_id = avatar.create_avatar_from_image(image_paths=test_images)
print(f"Avatar created with ID: {avatar_id}")

# Wait for processing and download the result
try:
    # Download the avatar to the current directory
    output_file = "hey.obj"
    print(f"Downloading avatar to {output_file}...")
    
    # This will poll until the avatar is ready, then download it
    downloaded_file = avatar.download_avatar(filename=output_file)
    
    print(f"Avatar successfully downloaded to: {downloaded_file}")
except Exception as e:
    print(f"Error downloading avatar: {str(e)}")
