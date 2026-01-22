
import streamlit as st
from ..ML_classification.unified_classifier import get_classifier


def ml_analysis_mode():
    """ML analysis and ingredient identification mode."""
    st.header("Ingredient Detection")

    if "extracted_ingredients" not in st.session_state or not st.session_state.get(
        "extracted_ingredients"
    ):
        st.warning("No extracted ingredients available.")
        if st.button("Back to Ingredient Selection"):
            st.session_state.selected_mode = "Select"
            st.rerun()
        return

    ingredients = st.session_state["extracted_ingredients"]
    
    # Get classifier and load model dynamically
    classifier = get_classifier()
    status = classifier.get_status()
    
    # Show model status
    if status["model_loaded"]:
        st.success("Real ML model loaded successfully")
        st.info(f"Using: {status['model_name']} on {status['device']}")
    else:
        st.warning("Real ML model not available - using fallback mode")
    
    # Display ingredients ready for analysis
    st.write("Ingredients ready for analysis:")
    cols = st.columns(min(len(ingredients), 4))
    
    for i, ingredient in enumerate(ingredients):
        with cols[i % len(cols)]:
            st.image(ingredient["image"], caption=f"Ingredient {ingredient['index']}")

    # Analysis button
    if st.button("Detect Ingredients", type="primary", use_container_width=True):
        run_ml_analysis(ingredients)

    # Display results if available
    if "ml_results" in st.session_state:
        display_ml_results(st.session_state["ml_results"], ingredients)


def run_ml_analysis(ingredients):
    """Run ML analysis using Hugging Face model."""
    classifier = get_classifier()
    
    with st.spinner("Running AI ingredient analysis..."):
        try:
            # Extract images from ingredients
            images = [ingredient["image"] for ingredient in ingredients]
            
            # Use the Hugging Face classifier
            predictions = classifier.classify_ingredients_batch(images)
            
            # Convert to the format expected by display function
            ml_results = []
            for i, preds in enumerate(predictions):
                if preds:  # If we have predictions
                    main_prediction = preds[0]
                    alternatives = preds[1:] if len(preds) > 1 else []
                    
                    ml_results.append({
                        "ingredient_id": f"ingredient_{ingredients[i].get('index', i)}",
                        "prediction": main_prediction["label"],
                        "model_used": "huggingface",
                        "alternatives": [
                            {
                                "ingredient": alt["label"]
                            } for alt in alternatives
                        ]
                    })
                else:
                    # Fallback if no predictions
                    ml_results.append({
                        "ingredient_id": f"ingredient_{ingredients[i].get('index', i)}",
                        "prediction": "unknown",
                        "model_used": "error",
                        "alternatives": []
                    })
            
            st.session_state["ml_results"] = ml_results
            st.success("Analysis complete")
            st.rerun()
            
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")


def display_ml_results(results, ingredients):
    """Display ML analysis results."""
    st.markdown("---")
    st.subheader("Detection Results")

    for i, result in enumerate(results):
        col1, col2 = st.columns(2)

        with col1:
            if i < len(ingredients):
                st.image(ingredients[i]["image"], width=100)

        with col2:
            st.write(f"**Ingredient {i+1}**")
            st.write(f"Prediction: **{result['prediction']}**")