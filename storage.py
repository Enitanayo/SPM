import streamlit as st
import requests
import base64
import io
from PIL import Image


class ImageStorage:
    def __init__(self):
        self.api_key = 'imgbb_api_key'
    
    def upload_image(self, image_file):
        """
        Upload image to ImgBB free hosting service
        Returns URL if successful, None otherwise
        """
        if self.api_key == "imgbb_api_key":
            st.error("Please set up your ImgBB API key in storage.py")
            return None
            
        try:
            # Convert to bytes
            img_bytes = image_file.getvalue()
            
            # Encode to base64
            encoded_image = base64.b64encode(img_bytes).decode()
            
            # Prepare API request
            url = "https://api.imgbb.com/1/upload"
            payload = {
                'key': self.api_key,
                'image': encoded_image,
                'expiration': 2592000
            }
            
            # Upload image
            response = requests.post(url, data=payload)
            result = response.json()
            
            if result.get('success'):
                return result['data']['url']
            else:
                st.error(f"Image upload failed: {result.get('error', {}).get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            st.error(f"Error uploading image: {str(e)}")
            return None
    
    def validate_image(self, image_file, max_size_mb=5):
        """Validate image file size and type"""
        # Check file size (5MB limit)
        if len(image_file.getvalue()) > max_size_mb * 1024 * 1024:
            return False, f"Image size must be less than {max_size_mb}MB"
        
        # Check file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        if image_file.type not in allowed_types:
            return False, "Only JPEG, PNG, and GIF images are allowed"
        
        return True, "Image is valid"

# Alternative: Local storage fallback (for development without API key)
class LocalImageStorage:
    def upload_image(self, image_file):
        """Store image locally and return a placeholder (for development only)"""
        st.warning("Using local image storage - images won't persist between sessions")
        return "https://via.placeholder.com/300x200?text=Lost+Found+Item"
    
    def validate_image(self, image_file, max_size_mb=5):
        """Validate image file size and type"""
        # Check file size (5MB limit)
        if len(image_file.getvalue()) > max_size_mb * 1024 * 1024:
            return False, f"Image size must be less than {max_size_mb}MB"
        
        # Check file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        if image_file.type not in allowed_types:
            return False, "Only JPEG, PNG, and GIF images are allowed"
        
        return True, "Image is valid"