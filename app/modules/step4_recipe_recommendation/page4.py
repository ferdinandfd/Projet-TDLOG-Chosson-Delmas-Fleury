import streamlit as st
from .recommender import recommend_recipes
import os
import sys

# Add config path for ingredient mapping  
config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config')
sys.path.append(config_path)

from ing_map import ingredients


def map_ml_predictions_to_standard_names(ml_predictions):
    """
    Map ML prediction names to standard ingredient names used in recipe matrix.
    """
    mapped_ingredients = []
    
    # Create reverse mapping from ing_map.py
    ml_to_standard = {}
    for category_name, category_ingredients in ingredients.items():
        for standard_name, variants in category_ingredients.items():
            # Add the standard name itself
            ml_to_standard[standard_name] = standard_name
            # Add all variants  
            for variant in variants:
                ml_to_standard[variant.lower()] = standard_name
    
    for prediction in ml_predictions:
        prediction_lower = prediction.lower().strip()
        
        # Direct mapping first
        if prediction_lower in ml_to_standard:
            mapped_name = ml_to_standard[prediction_lower]
            if mapped_name not in mapped_ingredients:
                mapped_ingredients.append(mapped_name)
        # Partial matching for ML predictions  
        elif prediction_lower == "bell_pepper":
            if "pepper" not in mapped_ingredients:
                mapped_ingredients.append("pepper")
        elif prediction_lower in ["potato", "potatoes"]:
            if "potato" not in mapped_ingredients:
                mapped_ingredients.append("potato")
        elif prediction_lower in ["tomato", "tomatoes"]:
            if "tomato" not in mapped_ingredients:
                mapped_ingredients.append("tomato")
        elif prediction_lower in ["onion", "onions"]:
            if "onion" not in mapped_ingredients:
                mapped_ingredients.append("onion")
        elif prediction_lower in ["carrot", "carrots"]:
            if "carrot" not in mapped_ingredients:
                mapped_ingredients.append("carrot")
        elif prediction_lower in ["mushroom", "mushrooms"]:
            if "mushroom" not in mapped_ingredients:
                mapped_ingredients.append("mushroom")
        else:
            # Use prediction as-is 
            if prediction_lower not in mapped_ingredients:
                mapped_ingredients.append(prediction_lower)
    
    return mapped_ingredients


def recipe_recommendation_mode():
    """Recipe recommendation based on identified ingredients."""
    st.header("Recipe Recommendations")

    if "ml_results" not in st.session_state or not st.session_state.get("ml_results"):
        st.warning("No ingredient analysis found. Please complete steps 1-3 first.")
        st.info("Steps: 1) Capture → 2) Select → 3) Detect → 4) Recommend")
        return

    # Get identified ingredients from ML results
    ml_predictions = [
        result["prediction"] for result in st.session_state["ml_results"]
        if result["prediction"] != "unknown"
    ]
    
    st.subheader("Your Identified Ingredients")
    st.write(f"**ML Predictions**: {', '.join(ml_predictions)}")
    
    # Map ML predictions to standard ingredient names
    mapped_ingredients = map_ml_predictions_to_standard_names(ml_predictions)
    st.write(f"**Mapped for Recipes**: {', '.join(mapped_ingredients)}")
    
    if not mapped_ingredients:
        st.warning("No ingredients could be mapped to recipe database.")
        return
    
    # Get recipe recommendations
    st.subheader("Recommended Recipes")
    
    try:
        # Use the existing recommendation system
        recommended_recipes = recommend_recipes(mapped_ingredients, num_recipes=10)
        
        if not recommended_recipes or all(score == 0 for _, score in recommended_recipes):
            st.warning("No recipes found with your ingredients.")
            st.info("Try different ingredients or check ingredient mapping.")
        else:
            # Display recommendations with scores
            for i, (recipe_name, score) in enumerate(recommended_recipes):
                if score > 0:  # Only show recipes with non-zero scores
                    with st.container():
                        st.markdown(f"**{i+1}. {recipe_name}**")
                        st.markdown(f"📊 Match Score: {score}")
                        st.markdown("---")
            
            # Debug information
            with st.expander("Debug Information"):
                st.write("**Recipe Scores** (top 15):")
                for recipe_name, score in recommended_recipes[:15]:
                    st.write(f"{recipe_name}: {score}")
                    
                st.write(f"**Total predictions**: {len(ml_predictions)}")
                st.write(f"**Mapped ingredients**: {len(mapped_ingredients)}")
                
    except Exception as e:
        st.error(f"Error generating recommendations: {str(e)}")
        st.write("Check that recipe matrix file exists and mappings are correct.")