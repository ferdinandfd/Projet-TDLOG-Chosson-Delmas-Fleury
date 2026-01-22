"""
Recipe Dataset Filter

This module filters the recipe dataset to match the cleaned ingredient matrix.
It ensures that only recipes present in the matrix are included in the final
recipe dataset, maintaining consistency between the matrix and recipe data.

The filtering process:
1. Loads the cleaned ingredient matrix
2. Loads the original recipe dataset
3. Filters recipes to match matrix rows
4. Saves the filtered recipe dataset
"""

import pandas as pd
import logging
from pathlib import Path

from ..config.settings import PreprocessingConfig

logger = logging.getLogger(__name__)


class RecipeFilter:
    """
    Filters recipe dataset to match the cleaned ingredient matrix.
    
    This class ensures consistency between the recipe data and the
    ingredient matrix by filtering recipes to match matrix dimensions.
    """
    
    def __init__(self, config: PreprocessingConfig):
        """Initialize the recipe filter with configuration."""
        self.config = config
        self.cleaned_matrix = None
        self.original_recipes = None
        self.filtered_recipes = None
        
    def load_cleaned_matrix(self) -> pd.DataFrame:
        """
        Load the cleaned ingredient matrix.
        
        Returns:
            Cleaned ingredient matrix DataFrame
        """
        try:
            path = self.config.CLEANED_MATRIX_PATH
            logger.info(f"Loading cleaned matrix from {path}")
            self.cleaned_matrix = pd.read_csv(path)
            logger.info(f"Matrix shape: {self.cleaned_matrix.shape}")
            return self.cleaned_matrix
        except FileNotFoundError:
            logger.error("Cleaned matrix file not found")
            raise
        except Exception as e:
            logger.error(f"Error loading cleaned matrix: {e}")
            raise
    
    def load_original_recipes(self) -> pd.DataFrame:
        """
        Load the original recipe dataset.
        
        Returns:
            Original recipe DataFrame
        """
        try:
            path = self.config.RAW_RECIPES_PATH
            logger.info(f"Loading original recipes from {path}")
            self.original_recipes = pd.read_csv(path)
            logger.info(f"Original recipes: {len(self.original_recipes)}")
            return self.original_recipes
        except FileNotFoundError:
            logger.error("Original recipe file not found")
            raise
        except Exception as e:
            logger.error(f"Error loading original recipes: {e}")
            raise
    
    def filter_recipes_to_matrix(self) -> pd.DataFrame:
        """
        Filter recipes to match the cleaned matrix dimensions.
        
        Returns:
            Filtered recipe DataFrame
        """
        if self.cleaned_matrix is None:
            raise ValueError("Cleaned matrix not loaded")
        if self.original_recipes is None:
            raise ValueError("Original recipes not loaded")
        
        logger.info("Filtering recipes to match matrix dimensions")
        
        # Get the number of recipes in the matrix
        matrix_recipe_count = len(self.cleaned_matrix)
        
        # Filter recipes to match matrix size
        if len(self.original_recipes) >= matrix_recipe_count:
            # Take the first N recipes to match matrix
            self.filtered_recipes = self.original_recipes.iloc[
                :matrix_recipe_count
            ].copy()
        else:
            # If we have fewer recipes than matrix rows, use all recipes
            logger.warning(
                f"Recipe count ({len(self.original_recipes)}) "
                f"is less than matrix rows ({matrix_recipe_count})"
            )
            self.filtered_recipes = self.original_recipes.copy()
        
        # Reset index to ensure clean indexing
        self.filtered_recipes = self.filtered_recipes.reset_index(drop=True)
        
        logger.info(f"Filtered to {len(self.filtered_recipes)} recipes")
        return self.filtered_recipes
    
    def validate_consistency(self) -> bool:
        """
        Validate that matrix and filtered recipes are consistent.
        
        Returns:
            True if consistent, False otherwise
        """
        if self.cleaned_matrix is None or self.filtered_recipes is None:
            return False
        
        matrix_rows = len(self.cleaned_matrix)
        recipe_rows = len(self.filtered_recipes)
        
        if matrix_rows == recipe_rows:
            logger.info(f"Validation passed: {matrix_rows} recipes matched")
            return True
        else:
            logger.error(
                f"Validation failed: {matrix_rows} matrix rows != "
                f"{recipe_rows} recipe rows"
            )
            return False
    
    def add_recipe_ids(self) -> pd.DataFrame:
        """
        Add consistent recipe IDs to the filtered dataset.
        
        Returns:
            Filtered recipes with recipe IDs
        """
        if self.filtered_recipes is None:
            raise ValueError("Filtered recipes not created")
        
        # Add recipe ID column if it doesn't exist
        if 'recipe_id' not in self.filtered_recipes.columns:
            self.filtered_recipes['recipe_id'] = range(
                len(self.filtered_recipes)
            )
            logger.info("Added recipe_id column")
        
        return self.filtered_recipes
    
    def save_filtered_recipes(self, output_path: str = None) -> None:
        """
        Save the filtered recipe dataset.
        
        Args:
            output_path: Optional custom output path
        """
        if self.filtered_recipes is None:
            raise ValueError("Filtered recipes not created")
        
        save_path = output_path or self.config.FILTERED_RECIPES_PATH
        
        logger.info(f"Saving filtered recipes to {save_path}")
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.filtered_recipes.to_csv(save_path, index=False)
        logger.info("Filtered recipes saved successfully")
    
    def get_filtering_report(self) -> dict:
        """
        Generate a report on the filtering process.
        
        Returns:
            Dictionary with filtering statistics
        """
        if self.original_recipes is None or self.filtered_recipes is None:
            return {}
        
        report = {
            'original_recipe_count': len(self.original_recipes),
            'filtered_recipe_count': len(self.filtered_recipes),
            'matrix_dimensions': (
                self.cleaned_matrix.shape if self.cleaned_matrix is not None
                else None
            ),
            'recipes_removed': (
                len(self.original_recipes) - len(self.filtered_recipes)
            ),
            'consistency_check': self.validate_consistency(),
            'recipe_columns': list(self.filtered_recipes.columns)
        }
        
        return report
    
    def run_full_pipeline(self) -> pd.DataFrame:
        """
        Run the complete recipe filtering pipeline.
        
        Returns:
            Filtered recipe dataset
        """
        logger.info("Starting recipe filtering pipeline")
        
        # Load data
        self.load_cleaned_matrix()
        self.load_original_recipes()
        
        # Filter recipes
        filtered_recipes = self.filter_recipes_to_matrix()
        
        # Add recipe IDs
        self.add_recipe_ids()
        
        # Validate consistency
        if not self.validate_consistency():
            logger.warning("Consistency validation failed")
        
        # Save filtered recipes
        self.save_filtered_recipes()
        
        # Generate and log report
        report = self.get_filtering_report()
        logger.info(f"Filtering report: {report}")
        
        logger.info("Recipe filtering pipeline complete")
        return filtered_recipes


def filter_recipes_to_matrix(
    config: PreprocessingConfig = None
) -> pd.DataFrame:
    """
    Convenience function to filter recipes to match matrix.
    
    Args:
        config: Optional preprocessing configuration
        
    Returns:
        Filtered recipe dataset
    """
    if config is None:
        config = PreprocessingConfig()
    
    filter_obj = RecipeFilter(config)
    return filter_obj.run_full_pipeline()


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    config = PreprocessingConfig()
    filtered_recipes = filter_recipes_to_matrix(config)
    
    print(f"Filtered recipes shape: {filtered_recipes.shape}")
    print("Recipe columns:")
    print(filtered_recipes.columns.tolist())
