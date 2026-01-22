"""
Configuration settings for the Recipe-Ingredient preprocessing pipeline.

This module contains all configurable parameters for data processing,
file paths, and pipeline settings.
"""

import os
from typing import Dict, List


class PreprocessingConfig:
    """
    Configuration class for the preprocessing pipeline.
    
    Contains all file paths, processing parameters, and pipeline settings
    used throughout the data preprocessing workflow.
    """
    
    # Input file paths
    RAW_RECIPES_PATH = "../datasets/marmiton_recipes.csv"
    
    # Output file paths
    OUTPUT_DIR = "output"
    RAW_MATRIX_PATH = os.path.join(OUTPUT_DIR, "recipe_ingredient_matrix_raw.csv")
    CLEANED_MATRIX_PATH = os.path.join(OUTPUT_DIR, "recipe_ingredient_matrix_VF.csv")
    FILTERED_RECIPES_PATH = os.path.join(OUTPUT_DIR, "marmiton_recipes_VF.csv")
    
    # Processing parameters
    MATRIX_DTYPE = int  # Data type for binary matrix values
    REMOVE_DUPLICATES = True  # Whether to remove duplicate recipes
    
    # Logging configuration
    LOG_LEVEL = "INFO"
    VERBOSE = True
    
    @classmethod
    def ensure_output_directory(cls):
        """Create output directory if it doesn't exist."""
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
    
    @classmethod
    def get_file_paths(cls) -> Dict[str, str]:
        """
        Get all file paths used in the pipeline.
        
        Returns:
            dict: Dictionary containing all file paths
        """
        return {
            "raw_recipes": cls.RAW_RECIPES_PATH,
            "raw_matrix": cls.RAW_MATRIX_PATH,
            "cleaned_matrix": cls.CLEANED_MATRIX_PATH,
            "filtered_recipes": cls.FILTERED_RECIPES_PATH
        }


# Pipeline step configuration
PIPELINE_STEPS = [
    "matrix_creation",
    "matrix_cleaning", 
    "recipe_filtering"
]

# Ingredient categories to remove during cleaning
INGREDIENTS_TO_REMOVE = [
    "colorant",
    "bouchées feuilletées", 
    "foie",
    "fumet"
]
