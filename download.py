import meshcapade
import os
import time

# Get API key from environment variable
api_key = os.environ.get('MESHCAPADE_API_KEY')
if not api_key:
    raise ValueError("MESHCAPADE_API_KEY environment variable is not set. Please set it before running this script.")

# Set API key
meshcapade.set_api_key(api_key)
# Define path to test images
image_folder = "/home/sagar/3d/meshcapade-sdk/test_images"
test_images = [
    os.path.join(image_folder, "image.jpg"),
]

# Create an Avatar
print("Creating a new avatar...")
avatar = meshcapade.Avatar(
    name="Emma",
    height=180,
    weight=75,
    gender="female"
)


# Wait for processing and download the result
try:
    # Download the avatar to the current directory
    output_file = "emma.obj"
    print(f"Downloading avatar to {output_file}...")
    
    # This will poll until the avatar is ready, then download it
    downloaded_file = avatar.download_avatar(avatar_id="5617fa78-92c6-4413-9da6-aa072bf3b935", filename=output_file)

    print(f"Avatar successfully downloaded to: {downloaded_file}")
except Exception as e:
    print(f"Error downloading avatar: {str(e)}")
