"""
Core preprocessing modules for recipe data processing.

Main modules:
- matrix_creator: Creates binary recipe-ingredient matrices
- matrix_cleaner: Cleans and standardizes matrices using ingredient mapping
- recipe_filter: Filters recipes to match cleaned matrix dimensions
- pipeline_runner: Orchestrates the complete preprocessing workflow
"""

from .matrix_creator import MatrixCreator, create_recipe_matrix
from .matrix_cleaner import MatrixCleaner, clean_ingredient_matrix
from .recipe_filter import RecipeFilter, filter_recipes_to_matrix
from .pipeline_runner import PreprocessingPipeline, run_preprocessing_pipeline

__all__ = [
    'MatrixCreator',
    'create_recipe_matrix',
    'MatrixCleaner',
    'clean_ingredient_matrix',
    'RecipeFilter',
    'filter_recipes_to_matrix',
    'PreprocessingPipeline',
    'run_preprocessing_pipeline'
]
