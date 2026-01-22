import pandas as pd 
import numpy as np
import sys
import os

# Define path but don't load immediately to avoid import issues
def get_matrix():
    """Load the recipe matrix on demand."""
    matrix_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'preprocessing', 'output', 'recipes_ingredients_matrix.csv')
    return pd.read_csv(matrix_path, index_col=0)

# Add config path for ingredient weights  
config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config')
sys.path.append(config_path)

try:
    from ingredient_weights import INGREDIENT_WEIGHTS
except ImportError:
    # Fallback weights if import fails
    INGREDIENT_WEIGHTS = {
        "meat": 5, "fish_seafood": 5, "vegetables": 4, "grains_legumes": 4,
        "fruits_nuts": 3, "dairy_eggs": 3, "sweets_baking": 3, "spices": 2,
        "liquids": 2, "cooking_bases": 2, "processed_foods": 2, "condiments": 1
    }


def compute_recipe_score(ingredients_available, recipe):
    """
    Computes weighted score of a recipe given a list of available ingredients.
    """
    matrix = get_matrix()  # Load matrix when needed
    score = 0
    
    for ingr in ingredients_available:
        if ingr in matrix.columns:
            # Get the value and convert to scalar if needed
            ingredient_value = matrix.loc[recipe, ingr]
            
            # Handle the case where it returns a Series
            if isinstance(ingredient_value, pd.Series):
                ingredient_value = ingredient_value.iloc[0]
            
            # Convert to int to avoid any ambiguity
            ingredient_value = int(ingredient_value)
            
            if ingredient_value == 1:
                # Get weight for this ingredient (default to 2 if not found)
                weight = INGREDIENT_WEIGHTS.get(ingr, 2)
                score += weight
                    
    return score


def recommend_recipes(ingredients_available, num_recipes):
    """
    Recommends the most adequate recipes according to a list of available
    ingredients using weighted scoring.
    """
    matrix = get_matrix()  # Load matrix when needed
    recipe_names = list(matrix.index)
    
    scores = {}
    for recipe in recipe_names:
        recipe_score = compute_recipe_score(ingredients_available, recipe)
        scores[recipe] = recipe_score
    sorted_recipes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_recipes[:num_recipes]
