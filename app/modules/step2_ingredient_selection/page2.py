import streamlit as st 
from datetime import datetime
from PIL import Image, ImageDraw

# Try to import streamlit_image_coordinates - graceful fallback if not available
CLICK_DETECTION_AVAILABLE = False
try:
    from streamlit_image_coordinates import streamlit_image_coordinates
    CLICK_DETECTION_AVAILABLE = True
except ImportError:
    streamlit_image_coordinates = None
    st.warning("streamlit_image_coordinates not available - using fallback mode")


def ingredient_selection_mode():
    """Interactive ingredient selection mode."""
    st.header("Select Your Ingredients")

    if (
        "current_image" not in st.session_state
        or st.session_state["current_image"] is None
    ):
        st.warning("No image captured yet. Please go to the Capture tab first.")
        st.info("Steps: 1) Capture → Take photo or upload image, 2) Select → Click on ingredients")
        return

    # Initialize session state
    if "selected_ingredients" not in st.session_state:
        st.session_state["selected_ingredients"] = []
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = (
            f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

    image = st.session_state["current_image"]

    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("Click on Ingredients You Want To Use")

        # Create annotated image
        display_image = image.copy()
        if st.session_state["selected_ingredients"]:
            draw = ImageDraw.Draw(display_image)
            for i, (x, y) in enumerate(st.session_state["selected_ingredients"]):
                # Draw a circle on each of the selected ingredients
                radius = 20
                draw.ellipse(
                    [x - radius, y - radius, x + radius, y + radius],
                    outline="red",
                    width=3,
                )
                # Draw ingredient number inside circle
                draw.text((x - 5, y - 5), str(i + 1), fill="red")

        # Interactive image (with click detection if available)
        if CLICK_DETECTION_AVAILABLE:
            try:
                value = streamlit_image_coordinates(
                    display_image, key="ingredient_selector"
                )

                if value is not None and "x" in value and "y" in value:
                    new_point = (int(value["x"]), int(value["y"]))
                    if new_point not in st.session_state["selected_ingredients"]:
                        st.session_state["selected_ingredients"].append(new_point)
                        st.rerun()
            except Exception as e:
                st.error(f"Click detection error: {e}")
                # Fallback to basic image display
                st.image(display_image, use_column_width=True)
        else:
            # Fallback: display image and manual coordinate input
            st.image(display_image, use_column_width=True)
            st.info("Click detection not available. Use manual input below.")
            
            # Manual coordinate input
            with st.expander("Add ingredient manually"):
                col_x, col_y = st.columns(2)
                with col_x:
                    x_coord = st.number_input("X coordinate", min_value=0, max_value=display_image.width, value=100)
                with col_y:
                    y_coord = st.number_input("Y coordinate", min_value=0, max_value=display_image.height, value=100)
                
                if st.button("Add Ingredient", key="manual_add"):
                    new_point = (int(x_coord), int(y_coord))
                    if new_point not in st.session_state["selected_ingredients"]:
                        st.session_state["selected_ingredients"].append(new_point)
                        st.rerun()

    with col2:

        # Default selection size
        selection_size = 180

        # Clear selections button
        if st.button("Clear All"):
            st.session_state["selected_ingredients"] = []
            st.rerun()

        # Number of selected ingredients
        st.metric("Selected Ingredients", len(st.session_state["selected_ingredients"]))

        # Extract ingredients
        if st.session_state["selected_ingredients"]:
            st.subheader("Extraction")
            
            if st.button("Extract All Ingredients", use_container_width=True):
                extract_ingredients(
                    image, st.session_state["selected_ingredients"], selection_size
                )

    # Show selected ingredients
    if st.session_state["selected_ingredients"]:
        st.subheader("Your Selected Ingredients :")

        cols = st.columns(min(len(st.session_state["selected_ingredients"]), 4))

        for i, (x, y) in enumerate(st.session_state["selected_ingredients"]):
            with cols[i % len(cols)]:
                # Extract preview
                half_size = selection_size // 2
                left = max(0, x - half_size)
                top = max(0, y - half_size)
                right = min(image.width, x + half_size)
                bottom = min(image.height, y + half_size)

                extracted = image.crop((left, top, right, bottom))
                st.image(extracted, caption=f"Ingredient n°{i+1}")


def extract_ingredients(image, coordinates, selection_size):
    """Extract and save ingredients from image."""
    saved_ingredients = []

    with st.spinner("Extracting ingredients..."):
        for i, (x, y) in enumerate(coordinates):
            # Extract ingredient region
            half_size = selection_size // 2
            left = max(0, x - half_size)
            top = max(0, y - half_size)
            right = min(image.width, x + half_size)
            bottom = min(image.height, y + half_size)

            extracted = image.crop((left, top, right, bottom))

            saved_ingredients.append(
                {
                    "index": i + 1,
                    "coordinates": (x, y),
                    "image": extracted,
                }
            )

    st.session_state["extracted_ingredients"] = saved_ingredients
    st.success(f"Extracted and saved {len(saved_ingredients)} ingredients!")
