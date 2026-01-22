import streamlit as st
from PIL import Image
from .image_utils import (
    optimize_image_for_processing,
    validate_image_format,
    clear_captured_image
)

def display_photo_capture_page():
    """Photo capture and upload functionality for ingredients."""
    
    st.header("Capture Your Ingredients")
    
    # Clear image button if image exists
    if st.session_state.get("current_image"):
        if st.button("Clear Image"):
            clear_captured_image()
            st.rerun()
    
    # Tab for each input method 
    tab1, tab2 = st.tabs(["Take Photo", "Upload Image"])
        
    with tab1:
        st.subheader("Camera Capture")
        image_file = st.camera_input("Take a picture of your ingredients")
        
        if image_file:
            image = Image.open(image_file).convert("RGBA")
            optimized_image = optimize_image_for_processing(image)
            
            st.session_state["current_image"] = optimized_image
            st.session_state["image_source"] = "camera"
            
            st.image(optimized_image, caption="Your ingredients photo", 
                    width="stretch")
    
    with tab2:
        st.subheader("Upload Image")
        uploaded_file = st.file_uploader(
            "Upload Image",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp']
        )
        
        if uploaded_file is not None:
            # Image Format error fallback 
            if not validate_image_format(uploaded_file):
                return False
            
            try:
                # Reset file pointer for reading
                uploaded_file.seek(0)
                image = Image.open(uploaded_file)
                
                # Get image info before optimization
                
                # Optimize image for processing
                optimized_image = optimize_image_for_processing(image)
                
                # Store in session state
                st.session_state["current_image"] = optimized_image
                st.session_state["image_source"] = "upload"
                st.session_state["uploaded_filename"] = uploaded_file.name
                
                # Display the uploaded image
                st.image(optimized_image, 
                         caption=f"Uploaded: {uploaded_file.name}",
                         width="stretch")
                                
            except Exception as e:
                st.error(f"Error loading image: {e}")

    return st.session_state.get("current_image") is not None
