"""
Utilities for handling captured and uploaded images in the recipe recommender app.
"""

import streamlit as st
from PIL import Image, ImageOps
import io


def resize_image_if_needed(image, max_size=(1024, 1024)):
    """
    Resize image if it's too large while maintaining aspect ratio.
    """
    if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
        image.thumbnail(max_size, Image.Resampling.LANCZOS) 
    return image


def validate_image_format(uploaded_file):
    """
    Validate that the uploaded file is a supported image format.
    Returns True if valid image format
    """
    try:
        image = Image.open(uploaded_file)
        # Try to verify the image
        image.verify()
        return True
    except Exception:
        return False

def optimize_image_for_processing(image):
    """
    Ensure RGB format and proper size before ML processing
    """
    # Convert to RGB if needed
    if image.mode != 'RGB':
        # Create white background for transparency
        if image.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'RGBA':
                background.paste(image, mask=image.split()[-1])
            else:
                background.paste(image)
            image = background
        else:
            image = image.convert('RGB')
    
    # Auto-orient based on EXIF data : for app use on mobile
    image = ImageOps.exif_transpose(image)
    
    # Resize if too large
    image = resize_image_if_needed(image, max_size=(800, 800))
    
    return image


def clear_captured_image():
    """Clear the currently captured image from session state."""
    keys_to_clear = ["current_image", "image_source", "uploaded_filename"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]