"""
Recipe-Ingredient Matrix Cleaner

This module cleans and aggregates the raw ingredient matrix by:
1. Mapping raw French ingredients to standardized categories
2. Consolidating similar ingredients into groups
3. Removing unmapped or irrelevant ingredients
4. Creating a cleaned matrix with meaningful ingredient categories

The cleaning process improves recommendation quality by reducing noise
and ensuring consistent ingredient representation across recipes.
"""

import pandas as pd
from typing import Dict, List
import logging
from pathlib import Path

from ..config.settings import PreprocessingConfig
from ..config.ingredient_mapping import INGREDIENTS

logger = logging.getLogger(__name__)


class MatrixCleaner:
    """
    Cleans and standardizes recipe-ingredient matrices.
    
    This class processes raw ingredient matrices by mapping French ingredient
    names to standardized categories and consolidating similar ingredients.
    """
    
    def __init__(self, config: PreprocessingConfig):
        """Initialize the matrix cleaner with configuration."""
        self.config = config
        self.raw_matrix = None
        self.cleaned_matrix = None
        self.ingredient_mapping = self._build_ingredient_mapping()
        
    def _build_ingredient_mapping(self) -> Dict[str, str]:
        """
        Build mapping from raw ingredients to standardized categories.
        
        Returns:
            Dictionary mapping raw ingredients to category names
        """
        mapping = {}
        
        for category, ingredient_groups in INGREDIENTS.items():
            if category == "remove":
                # Mark ingredients to be removed
                for ingredient in ingredient_groups:
                    mapping[ingredient] = None
                continue
                
            for group_name, raw_ingredients in ingredient_groups.items():
                for raw_ingredient in raw_ingredients:
                    mapping[raw_ingredient] = group_name
                    
        logger.info(f"Built mapping for {len(mapping)} ingredients")
        return mapping
    
    def load_raw_matrix(self) -> pd.DataFrame:
        """
        Load the raw ingredient matrix from CSV.
        
        Returns:
            Raw ingredient matrix DataFrame
        """
        try:
            path = self.config.RAW_MATRIX_PATH
            logger.info(f"Loading raw matrix from {path}")
            self.raw_matrix = pd.read_csv(path)
            logger.info(f"Loaded matrix with shape: {self.raw_matrix.shape}")
            return self.raw_matrix
        except FileNotFoundError:
            logger.error("Raw matrix file not found")
            raise
        except Exception as e:
            logger.error(f"Error loading raw matrix: {e}")
            raise
    
    def identify_unmapped_ingredients(self) -> List[str]:
        """
        Identify ingredients in the matrix that are not mapped.
        
        Returns:
            List of unmapped ingredient names
        """
        if self.raw_matrix is None:
            raise ValueError("Raw matrix not loaded")
            
        matrix_ingredients = set(self.raw_matrix.columns)
        mapped_ingredients = set(self.ingredient_mapping.keys())
        unmapped = list(matrix_ingredients - mapped_ingredients)
        
        logger.info(f"Found {len(unmapped)} unmapped ingredients")
        if unmapped:
            logger.warning(f"Unmapped ingredients: {unmapped[:10]}...")
            
        return unmapped
    
    def map_ingredients_to_categories(self) -> pd.DataFrame:
        """
        Map raw ingredients to standardized categories.
        
        Returns:
            DataFrame with ingredients mapped to categories
        """
        if self.raw_matrix is None:
            raise ValueError("Raw matrix not loaded")
        
        logger.info("Mapping ingredients to standardized categories")
        
        # Create mapping for matrix columns
        column_mapping = {}
        ingredients_to_remove = []
        
        for ingredient in self.raw_matrix.columns:
            if ingredient in self.ingredient_mapping:
                mapped_category = self.ingredient_mapping[ingredient]
                if mapped_category is None:
                    # Mark for removal
                    ingredients_to_remove.append(ingredient)
                else:
                    column_mapping[ingredient] = mapped_category
            else:
                # Keep unmapped ingredients for now
                column_mapping[ingredient] = ingredient
        
        # Remove ingredients marked for removal
        if ingredients_to_remove:
            logger.info(f"Removing {len(ingredients_to_remove)} ingredients")
            matrix_filtered = self.raw_matrix.drop(
                columns=ingredients_to_remove, errors='ignore'
            )
        else:
            matrix_filtered = self.raw_matrix.copy()
        
        # Rename columns to standardized categories
        matrix_mapped = matrix_filtered.rename(columns=column_mapping)
        
        logger.info(f"Mapped matrix shape: {matrix_mapped.shape}")
        return matrix_mapped
    
    def aggregate_duplicate_categories(
        self, mapped_matrix: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Aggregate columns with the same category name.
        
        Args:
            mapped_matrix: Matrix with mapped ingredient categories
            
        Returns:
            Matrix with aggregated duplicate categories
        """
        logger.info("Aggregating duplicate ingredient categories")
        
        # Group columns by name and sum values
        aggregated_matrix = mapped_matrix.groupby(
            mapped_matrix.columns, axis=1
        ).max()
        
        # Ensure values remain binary (0 or 1)
        aggregated_matrix = (aggregated_matrix > 0).astype(int)
        
        logger.info(f"Aggregated matrix shape: {aggregated_matrix.shape}")
        return aggregated_matrix
    
    def remove_empty_columns(self, matrix: pd.DataFrame) -> pd.DataFrame:
        """
        Remove columns (ingredients) that don't appear in any recipe.
        
        Args:
            matrix: Input matrix
            
        Returns:
            Matrix without empty columns
        """
        # Find columns with at least one occurrence
        non_empty_columns = matrix.columns[matrix.sum() > 0]
        filtered_matrix = matrix[non_empty_columns]
        
        removed_count = len(matrix.columns) - len(filtered_matrix.columns)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} empty ingredient columns")
        
        return filtered_matrix
    
    def clean_matrix(self) -> pd.DataFrame:
        """
        Run the complete matrix cleaning pipeline.
        
        Returns:
            Cleaned and standardized ingredient matrix
        """
        logger.info("Starting matrix cleaning pipeline")
        
        # Load raw matrix
        if self.raw_matrix is None:
            self.load_raw_matrix()
        
        # Identify unmapped ingredients for reporting
        self.identify_unmapped_ingredients()
        
        # Map ingredients to categories
        mapped_matrix = self.map_ingredients_to_categories()
        
        # Aggregate duplicate categories
        aggregated_matrix = self.aggregate_duplicate_categories(mapped_matrix)
        
        # Remove empty columns
        cleaned_matrix = self.remove_empty_columns(aggregated_matrix)
        
        self.cleaned_matrix = cleaned_matrix
        
        logger.info("Matrix cleaning complete")
        logger.info(f"Final shape: {cleaned_matrix.shape}")
        
        original_count = self.raw_matrix.shape[1]
        final_count = cleaned_matrix.shape[1]
        logger.info(
            f"Reduced from {original_count} to {final_count} ingredients"
        )
        
        return cleaned_matrix
    
    def save_cleaned_matrix(self, output_path: str = None) -> None:
        """
        Save the cleaned matrix to CSV.
        
        Args:
            output_path: Optional custom output path
        """
        if self.cleaned_matrix is None:
            raise ValueError("Matrix not cleaned. Call clean_matrix() first.")
        
        save_path = output_path or self.config.CLEANED_MATRIX_PATH
        
        logger.info(f"Saving cleaned matrix to {save_path}")
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.cleaned_matrix.to_csv(save_path, index=False)
        logger.info("Cleaned matrix saved successfully")
    
    def get_cleaning_report(self) -> Dict:
        """
        Generate a report on the cleaning process.
        
        Returns:
            Dictionary with cleaning statistics
        """
        if self.raw_matrix is None or self.cleaned_matrix is None:
            return {}
        
        unmapped = self.identify_unmapped_ingredients()
        
        report = {
            'original_shape': self.raw_matrix.shape,
            'cleaned_shape': self.cleaned_matrix.shape,
            'ingredients_removed': (self.raw_matrix.shape[1] -
                                    self.cleaned_matrix.shape[1]),
            'unmapped_ingredients': len(unmapped),
            'unmapped_list': unmapped[:10],  # First 10 for brevity
            'ingredient_categories': list(self.cleaned_matrix.columns),
            'matrix_density_original': (
                self.raw_matrix.sum().sum() /
                (self.raw_matrix.shape[0] * self.raw_matrix.shape[1])
            ),
            'matrix_density_cleaned': (
                self.cleaned_matrix.sum().sum() /
                (self.cleaned_matrix.shape[0] * self.cleaned_matrix.shape[1])
            )
        }
        
        return report
    
    def run_full_pipeline(self) -> pd.DataFrame:
        """
        Run the complete cleaning pipeline and save results.
        
        Returns:
            Cleaned ingredient matrix
        """
        # Clean matrix
        cleaned_matrix = self.clean_matrix()
        
        # Save results
        self.save_cleaned_matrix()
        
        # Generate and log report
        report = self.get_cleaning_report()
        logger.info(f"Cleaning report: {report}")
        
        return cleaned_matrix


def clean_ingredient_matrix(
    config: PreprocessingConfig = None
) -> pd.DataFrame:
    """
    Convenience function to clean ingredient matrix.
    
    Args:
        config: Optional preprocessing configuration
        
    Returns:
        Cleaned ingredient matrix
    """
    if config is None:
        config = PreprocessingConfig()
    
    cleaner = MatrixCleaner(config)
    return cleaner.run_full_pipeline()


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    config = PreprocessingConfig()
    cleaned_matrix = clean_ingredient_matrix(config)
    
    print(f"Cleaned matrix shape: {cleaned_matrix.shape}")
    print("Sample of cleaned ingredients:")
    print(cleaned_matrix.columns[:10].tolist())
