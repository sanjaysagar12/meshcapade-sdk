# MeshCapade Python SDK

A Python client for interacting with the MeshCapade API, allowing you to create and manage 3D avatars.

## Installation

```bash
git clone https://github.com/sanjaysagar/meshcapade-sdk.git
cd meshcapade-sdk-python
pip install -e .
```

## Getting Started

```python
import os
import meshcapade
from meshcapade.exceptions import APIError

# Set your API key
meshcapade.set_api_key("your_api_key")

# Create an avatar
avatar = meshcapade.Avatar()
avatar.set_name("My Avatar")
avatar.set_height(175)  # cm
avatar.set_weight(70)   # kg
avatar.set_gender("male")

# Create avatar from images
try:
    avatar_id = avatar.create_avatar_from_image(image_paths=["path/to/image1.jpg", "path/to/image2.jpg"])
    print(f"Avatar created with ID: {avatar_id}")
    
    # Download the avatar model
    avatar.download_avatar(filename="my_avatar.obj")
    
except APIError as e:
    print(f"API Error: {e}")
```

## Features

- Create, retrieve, update, and delete avatars
- Upload images to generate avatars
- Download 3D avatar models
- List all avatars