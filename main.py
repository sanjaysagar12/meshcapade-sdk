"""
Example usage of the MeshCapade SDK
"""

import os
import time
import logging
import meshcapade
from dotenv import load_dotenv
from meshcapade.exceptions import APIError, TimeoutError, ValidationError

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("meshcapade-example")

# Load environment variables from .env file
load_dotenv()

def main():
    # Get API key from environment variable
    api_key = os.environ.get('MESHCAPADE_API_KEY')
    if not api_key:
        raise ValueError("MESHCAPADE_API_KEY environment variable is not set. Please set it before running this script.")

    # Set API key
    meshcapade.set_api_key(api_key)
    
    # Define path to test images
    image_folder = os.path.join(os.path.dirname(__file__), "test_images")
    # Make sure the test_images folder exists
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)
        
    test_image = os.path.join(image_folder, "woman.jpg")
    # Check if the test image exists
    if not os.path.exists(test_image):
        logger.error(f"Test image not found at {test_image}")
        logger.info("Please place a test image in the test_images folder or update the path")
        return
        
    test_images = [test_image]

    # Create an Avatar
    logger.info("Creating a new avatar...")
    try:
        avatar = meshcapade.Avatar()
        avatar.set_name("Test Avatar")
        avatar.set_height(165)
        avatar.set_weight(55)
        avatar.set_gender("female")

        # Generate the avatar from images
        logger.info("Generating avatar from images...")
        avatar_id = avatar.create_avatar_from_image(image_paths=test_images)
        logger.info(f"Avatar created with ID: {avatar_id}")

        # Wait for processing and download the result
        output_file = "output_avatar.obj"
        logger.info(f"Downloading avatar to {output_file}...")
        
        # This will poll until the avatar is ready, then download it
        downloaded_file = avatar.download_avatar(filename=output_file)
        
        logger.info(f"Avatar successfully downloaded to: {downloaded_file}")
       
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
    except APIError as e:
        logger.error(f"API error: {str(e)}")
    except TimeoutError as e:
        logger.error(f"Timeout error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
