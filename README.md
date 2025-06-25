# Meshcapade Python SDK Documentation

## Introduction

The Meshcapade Python SDK is a client library that enables developers to interact with the Meshcapade API for creating and managing 3D avatars. The SDK provides a straightforward interface to create avatars from images or body measurements, manage existing avatars, and download 3D models.

## Installation

To install the Meshcapade SDK, follow these steps:

```bash
git clone https://github.com/sanjaysagar12/meshcapade-sdk.git
cd meshcapade-sdk
pip install -e .
```

## Authentication

Before using the SDK, you need to set your Meshcapade API key:

```python
import meshcapade

# Set your API key
meshcapade.set_api_key("your_api_key")
```

You can also store your API key in an environment variable named `MESHCAPADE_API_KEY` and load it using:

```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.environ.get('MESHCAPADE_API_KEY')
meshcapade.set_api_key(api_key)
```

## Creating Avatars

The SDK provides two main methods for creating avatars:

### 1. Creating Avatars from Images

```python
import meshcapade
from meshcapade.exceptions import APIError

# Set your API key
meshcapade.set_api_key("your_api_key")

# Create an avatar instance and set properties
avatar = meshcapade.Avatar()
avatar.set_name("My Avatar")  # or use avatar.name = "My Avatar"
avatar.set_height(175)        # in cm
avatar.set_weight(70)         # in kg
avatar.set_gender("male")     # must be "male" or "female"

try:
    # Create avatar from one or more images
    image_paths = ["path/to/image1.jpg", "path/to/image2.jpg"]
    avatar_id = avatar.create_avatar_from_image(image_paths=image_paths)
    print(f"Avatar created with ID: {avatar_id}")
    
    # Download the avatar model
    downloaded_file = avatar.download_avatar(filename="my_avatar.obj")
    print(f"Avatar downloaded to: {downloaded_file}")
    
except APIError as e:
    print(f"API Error: {e}")
```

### 2. Creating Avatars from Body Measurements

```python
import meshcapade
from meshcapade.exceptions import APIError, ValidationError

# Set your API key
meshcapade.set_api_key("your_api_key")

# Create an avatar instance
avatar = meshcapade.Avatar()

try:
    # Option 1: Provide minimal measurements
    avatar.set_name("Measurement Avatar")
    avatar.set_gender("female")
    avatar.set_height(165)  # cm
    avatar.set_weight(60)   # kg
    
    avatar_id = avatar.create_avatar_from_measurements()
    print(f"Simple measurement avatar created with ID: {avatar_id}")
    
    # Option 2: Provide detailed measurements
    measurements = {
        "Height": 180,         # cm
        "Weight": 70,          # kg
        "Bust_girth": 95,      # cm
        "Ankle_girth": 22,     # cm
        "Thigh_girth": 55,     # cm
        "Waist_girth": 75,     # cm
        "Armscye_girth": 40,   # cm
        "Top_hip_girth": 90,   # cm
        "Neck_base_girth": 36, # cm
        "Shoulder_length": 15, # cm
        "Lower_arm_length": 25,# cm
        "Upper_arm_length": 30,# cm
        "Inside_leg_height": 80 # cm
    }
    
    avatar_id2 = avatar.create_avatar_from_measurements(
        name="Detailed Measurements",
        gender="female",
        measurements=measurements
    )
    print(f"Detailed measurement avatar created with ID: {avatar_id2}")
    
    # Download the avatar model
    avatar.download_avatar(avatar_id=avatar_id2, filename="measurements_avatar.obj")
    
except (APIError, ValidationError) as e:
    print(f"Error: {e}")
```

### 3. Creating a Predefined Avatar

The SDK also includes a convenience method to create an avatar with predefined measurements:

```python
import meshcapade

# Set your API key
meshcapade.set_api_key("your_api_key")

avatar = meshcapade.Avatar()
avatar_id = avatar.create_predefined_avatar()
print(f"Predefined avatar created with ID: {avatar_id}")
```

## Managing Avatars

The SDK provides several methods to manage your avatars:

### Retrieving Avatar Information

```python
# Get information about a specific avatar
avatar_data = avatar.get_avatar(avatar_id="your_avatar_id")
print(avatar_data)
```

### Listing All Avatars

```python
# List all your avatars (with pagination)
avatars = avatar.list_avatars(page=1, page_size=10)
print(f"Found {len(avatars.get('data', []))} avatars")
```

### Downloading an Avatar

```python
# Download a specific avatar by ID
try:
    file_path = avatar.download_avatar(
        avatar_id="your_avatar_id",
        filename="downloaded_avatar.obj",
        polling_interval=5,    # seconds between status checks 
        max_retries=60         # maximum number of status checks (5 sec * 60 = 5 min timeout)
    )
    print(f"Avatar downloaded to {file_path}")
except meshcapade.TimeoutError:
    print("Avatar processing timed out")
except meshcapade.APIError as e:
    print(f"Error: {e}")
```

### Deleting an Avatar

```python
# Delete an avatar
deletion_response = avatar.delete_avatar(avatar_id="your_avatar_id")
print("Avatar deleted successfully")
```

## Error Handling

The SDK provides several custom exception types to help with error handling:

```python
from meshcapade.exceptions import (
    MeshCapadeError,      # Base exception for all SDK errors
    AuthenticationError,  # Authentication issues (invalid API key)
    APIError,             # API request errors
    ValidationError,      # Input validation errors
    ResourceNotFoundError,# Resource not found (e.g., avatar not found)
    TimeoutError          # Operation timeout
)

try:
    # SDK operations...
    avatar_id = avatar.create_avatar_from_image(image_paths=["image.jpg"])
    
except ValidationError as e:
    print(f"Input validation error: {e}")
    
except AuthenticationError as e:
    print(f"Authentication error: {e}. Please check your API key.")
    
except APIError as e:
    print(f"API error (status: {e.status_code}): {e}")
    
except ResourceNotFoundError as e:
    print(f"Resource not found: {e}")
    
except TimeoutError as e:
    print(f"Operation timed out: {e}")
    
except MeshCapadeError as e:
    print(f"General SDK error: {e}")
```

## Complete Example

Here's a complete example that demonstrates creating an avatar from an image, waiting for processing, and downloading the result:

```python
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
        raise ValueError("MESHCAPADE_API_KEY environment variable is not set")

    # Set API key
    meshcapade.set_api_key(api_key)
    
    # Path to image
    image_path = "path/to/your/image.jpg"
    if not os.path.exists(image_path):
        logger.error(f"Image not found at {image_path}")
        return
        
    try:
        logger.info("Creating a new avatar...")
        
        # Initialize avatar with properties
        avatar = meshcapade.Avatar()
        avatar.set_name("Test Avatar")
        avatar.set_height(175)
        avatar.set_weight(70)
        avatar.set_gender("male")

        # Generate avatar from image
        logger.info("Generating avatar from image...")
        avatar_id = avatar.create_avatar_from_image(image_paths=[image_path])
        logger.info(f"Avatar created with ID: {avatar_id}")

        # Download the avatar (this will automatically poll until the avatar is ready)
        output_file = "my_avatar.obj"
        logger.info(f"Downloading avatar to {output_file}...")
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
```

## API Reference

### Avatar Class Methods

| Method | Description |
|--------|-------------|
| `__init__(api_key=None, api_url=None)` | Initialize Avatar class with optional API key and URL |
| `set_name(value)` or `name = value` | Set avatar name |
| `set_height(value)` or `height = value` | Set avatar height in cm (must be positive integer) |
| `set_weight(value)` or `weight = value` | Set avatar weight in kg (must be positive integer) |
| `set_gender(value)` or `gender = value` | Set avatar gender ("male" or "female") |
| `create_avatar_from_image(image_paths=None)` | Create avatar from images |
| `create_avatar_from_measurements(name=None, gender=None, measurements=None)` | Create avatar from body measurements |
| `create_predefined_avatar()` | Create avatar with predefined measurements |
| `get_avatar(avatar_id=None)` | Get avatar information |
| `download_avatar(avatar_id=None, filename="avatar.obj", polling_interval=5, max_retries=60)` | Download avatar 3D model |
| `delete_avatar(avatar_id=None)` | Delete avatar |
| `list_avatars(page=1, page_size=10)` | List all avatars |

### Measurement Parameters

When creating an avatar from measurements, you can provide the following parameters:

| Parameter | Description | Unit |
|-----------|-------------|------|
| Height | Overall height | cm |
| Weight | Weight | kg |
| Bust_girth | Circumference around chest at fullest part | cm |
| Ankle_girth | Circumference around ankle | cm |
| Thigh_girth | Circumference around thigh | cm |
| Waist_girth | Circumference around waist | cm |
| Armscye_girth | Circumference around armhole | cm |
| Top_hip_girth | Circumference around top of hips | cm |
| Neck_base_girth | Circumference around base of neck | cm |
| Shoulder_length | Length of shoulder | cm |
| Lower_arm_length | Length of lower arm | cm |
| Upper_arm_length | Length of upper arm | cm |
| Inside_leg_height | Inseam length | cm |

## Advanced Configuration

You can set a custom API URL if needed:

```python
# Set custom API URL (for testing or specific endpoints)
meshcapade.set_api_url("https://custom-api.meshcapade.com/api/v1")
```

## Internal SDK Architecture

The SDK consists of the following main components:

1. `meshcapade/__init__.py` - Main package initialization, API configuration, and imports
2. `meshcapade/client.py` - Base client for API communication
3. `meshcapade/avatar.py` - Avatar class for creating and managing avatars
4. `meshcapade/exceptions.py` - Custom exception types

The `BaseClient` class handles API requests with proper error handling, while the `Avatar` class provides high-level methods for avatar operations.
