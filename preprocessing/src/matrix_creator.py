"""
Recipe-Ingredient Matrix Creator

This module creates a binary matrix indicating which ingredients are present
in each recipe. Each row represents a recipe and each column represents an
ingredient. A value of 1 indicates the ingredient is used, 0 otherwise.

The process involves:
1. Loading recipe data from CSV
2. Parsing ingredient lists from text
3. Creating binary matrix based on ingredient presence
4. Saving the matrix for further processing
"""

import pandas as pd
import numpy as np
from typing import List, Set
import logging
from pathlib import Path

from ..config.settings import PreprocessingConfig

logger = logging.getLogger(__name__)


class MatrixCreator:
    """
    Creates recipe-ingredient binary matrices from recipe data.
    
    This class handles the conversion of recipe text data into structured
    binary matrices where each recipe is mapped to its constituent ingredients.
    """
    
    def __init__(self, config: PreprocessingConfig):
        """Initialize the matrix creator with configuration."""
        self.config = config
        self.recipes_df = None
        self.ingredient_matrix = None
        self.ingredient_columns = None
        
    def load_recipe_data(self) -> pd.DataFrame:
        """
        Load recipe data from CSV file.
        
        Returns:
            DataFrame with recipe information including ingredients
        """
        try:
            path = self.config.RAW_RECIPES_PATH
            logger.info(f"Loading recipe data from {path}")
            self.recipes_df = pd.read_csv(path)
            logger.info(f"Loaded {len(self.recipes_df)} recipes")
            return self.recipes_df
        except FileNotFoundError:
            logger.error(f"Recipe file not found: {path}")
            raise
        except Exception as e:
            logger.error(f"Error loading recipe data: {e}")
            raise
    
    def extract_ingredients_from_text(self, ingredient_text: str) -> Set[str]:
        """
        Extract individual ingredients from ingredient text.
        
        Args:
            ingredient_text: Raw ingredient text from recipe
            
        Returns:
            Set of cleaned ingredient names
        """
        if pd.isna(ingredient_text):
            return set()
        
        # Basic text cleaning and ingredient extraction
        ingredients = str(ingredient_text).lower()
        
        # Remove common quantity indicators and split by commas
        ingredients = ingredients.replace(' - ', ', ')
        ingredient_list = [ing.strip() for ing in ingredients.split(',')]
        
        # Remove empty strings and clean each ingredient
        cleaned_ingredients = set()
        for ingredient in ingredient_list:
            if ingredient and len(ingredient) > 1:
                # Remove numbers and common quantity words
                stop_words = ['de', 'du', 'des', 'la', 'le', 'les']
                words = [word for word in ingredient.split()
                         if not word.isdigit() and word not in stop_words]
                cleaned = ' '.join(words)
                if cleaned:
                    cleaned_ingredients.add(cleaned.strip())
        
        return cleaned_ingredients
    
    def collect_all_ingredients(self) -> List[str]:
        """
        Collect all unique ingredients from all recipes.
        
        Returns:
            Sorted list of all unique ingredients
        """
        logger.info("Collecting all unique ingredients from recipes")
        all_ingredients = set()
        
        for _, recipe in self.recipes_df.iterrows():
            recipe_ingredients = self.extract_ingredients_from_text(
                recipe.get('ingredients', '')
            )
            all_ingredients.update(recipe_ingredients)
        
        # Sort ingredients alphabetically for consistency
        sorted_ingredients = sorted(list(all_ingredients))
        logger.info(f"Found {len(sorted_ingredients)} unique ingredients")
        
        return sorted_ingredients
    
    def create_binary_matrix(self) -> pd.DataFrame:
        """
        Create binary recipe-ingredient matrix.
        
        Returns:
            DataFrame where rows are recipes and columns are ingredients,
            with 1 indicating ingredient presence, 0 otherwise
        """
        if self.recipes_df is None:
            msg = "Recipe data not loaded. Call load_recipe_data() first."
            raise ValueError(msg)
        
        logger.info("Creating binary recipe-ingredient matrix")
        
        # Get all unique ingredients
        self.ingredient_columns = self.collect_all_ingredients()
        
        # Initialize matrix with zeros
        num_recipes = len(self.recipes_df)
        num_ingredients = len(self.ingredient_columns)
        matrix = np.zeros((num_recipes, num_ingredients))
        
        # Fill matrix with ingredient presence
        for recipe_idx, (_, recipe) in enumerate(self.recipes_df.iterrows()):
            recipe_ingredients = self.extract_ingredients_from_text(
                recipe.get('ingredients', '')
            )
            
            for ingredient_idx, ingredient in enumerate(
                self.ingredient_columns
            ):
                if ingredient in recipe_ingredients:
                    matrix[recipe_idx, ingredient_idx] = 1
        
        # Create DataFrame with proper column names
        self.ingredient_matrix = pd.DataFrame(
            matrix,
            columns=self.ingredient_columns,
            index=self.recipes_df.index
        )
        
        shape = self.ingredient_matrix.shape
        logger.info(f"Created matrix with shape: {shape}")
        return self.ingredient_matrix
    
    def save_matrix(self, output_path: str = None) -> None:
        """
        Save the ingredient matrix to CSV.
        
        Args:
            output_path: Optional custom output path
        """
        if self.ingredient_matrix is None:
            msg = "Matrix not created. Call create_binary_matrix() first."
            raise ValueError(msg)
        
        save_path = output_path or self.config.RAW_MATRIX_PATH
        
        logger.info(f"Saving matrix to {save_path}")
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.ingredient_matrix.to_csv(save_path, index=False)
        logger.info("Matrix saved successfully")
    
    def get_matrix_statistics(self) -> dict:
        """
        Get statistics about the created matrix.
        
        Returns:
            Dictionary with matrix statistics
        """
        if self.ingredient_matrix is None:
            return {}
        
        total_elements = (len(self.ingredient_matrix) *
                          len(self.ingredient_columns))
        matrix_sum = self.ingredient_matrix.sum().sum()
        
        stats = {
            'total_recipes': len(self.ingredient_matrix),
            'total_ingredients': len(self.ingredient_columns),
            'matrix_density': matrix_sum / total_elements,
            'avg_ingredients_per_recipe': (
                self.ingredient_matrix.sum(axis=1).mean()
            ),
            'most_common_ingredients': (
                self.ingredient_matrix.sum()
                .sort_values(ascending=False)
                .head(10)
                .to_dict()
            )
        }
        
        return stats
    
    def run_full_pipeline(self) -> pd.DataFrame:
        """
        Run the complete matrix creation pipeline.
        
        Returns:
            Created ingredient matrix
        """
        logger.info("Starting matrix creation pipeline")
        
        # Load data
        self.load_recipe_data()
        
        # Create matrix
        matrix = self.create_binary_matrix()
        
        # Save matrix
        self.save_matrix()
        
        # Log statistics
        stats = self.get_matrix_statistics()
        logger.info(f"Matrix creation complete. Statistics: {stats}")
        
        return matrix


def create_recipe_matrix(config: PreprocessingConfig = None) -> pd.DataFrame:
    """
    Convenience function to create recipe-ingredient matrix.
    
    Args:
        config: Optional preprocessing configuration
        
    Returns:
        Created ingredient matrix
    """
    if config is None:
        config = PreprocessingConfig()
    
    creator = MatrixCreator(config)
    return creator.run_full_pipeline()


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    config = PreprocessingConfig()
    matrix = create_recipe_matrix(config)
    
    print(f"Created matrix with shape: {matrix.shape}")
    print("First 5 recipes and ingredients:")
    print(matrix.iloc[:5, :5])
