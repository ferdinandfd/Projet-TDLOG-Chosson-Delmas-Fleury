import streamlit as st
import os
import sys
from style.custom_styling import apply_custom_css

# Add paths for module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import module functions
from modules.step1_photo_capture.capture import display_photo_capture_page as photo_capture_mode
from modules.step2_ingredient_selection.page2 import ingredient_selection_mode
from modules.step3_ingrdient_recognition.manual_confirm.page3 import ml_analysis_mode
from modules.step4_recipe_recommendation.page4 import recipe_recommendation_mode


def main():
    st.set_page_config(page_title="Recipe Recommender", layout="wide")

    # Apply custom styling
    apply_custom_css()

    st.title("Smart Recipe Recommender")

    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Capture", use_container_width=True):
            st.session_state.selected_mode = "Capture"
    with col2:
        if st.button("Select", use_container_width=True):
            st.session_state.selected_mode = "Select"
    with col3:
        if st.button("Detect", use_container_width=True):
            st.session_state.selected_mode = "Detect"
    with col4:
        if st.button("Recommend", use_container_width=True):
            st.session_state.selected_mode = "Recommend"
    
    # Initialize mode if not set
    if "selected_mode" not in st.session_state:
        st.session_state.selected_mode = "Capture"
    
    # Sidebar for navigation (backup)
    with st.sidebar:
        st.header("Navigation")
        sidebar_mode = st.selectbox(
            "Choose your mode:",
            [
                "Capture",
                "Select", 
                "Detect",
                "Recommend",
            ],
            index=["Capture", "Select", "Detect", "Recommend"].index(st.session_state.selected_mode)
        )
        
        # Update selected mode if sidebar selection changes
        if sidebar_mode != st.session_state.selected_mode:
            st.session_state.selected_mode = sidebar_mode

        # Check for missing dependencies silently
        pass
    
    # Use the selected mode
    mode = st.session_state.selected_mode
    st.markdown("---")

    if mode == "Capture":
        photo_capture_mode()
    elif mode == "Select":
        ingredient_selection_mode()
    elif mode == "Detect":
        ml_analysis_mode()
    elif mode == "Recommend":
        recipe_recommendation_mode()

if __name__ == "__main__":
    main()