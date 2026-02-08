"""
Preprocessing Package for Recipe Recommender

This package contains modules for preprocessing recipe and ingredient data:

- config/: Configuration files and ingredient mappings
- src/: Core preprocessing modules
- output/: Generated outputs and reports

Main modules:
- matrix_creator: Creates recipe-ingredient binary matrices
- matrix_cleaner: Cleans and standardizes ingredient matrices 
- recipe_filter: Filters recipes to match cleaned matrices
- pipeline_runner: Orchestrates the complete preprocessing workflow

Usage:
    from preprocessing.src.pipeline_runner import run_preprocessing_pipeline
    success = run_preprocessing_pipeline()
"""

from .config.settings import PreprocessingConfig

__version__ = "1.0.0"
__author__ = "Recipe Recommender Team"

# Export main pipeline function
from .src.pipeline_runner import run_preprocessing_pipeline

__all__ = [
    'PreprocessingConfig',
    'run_preprocessing_pipeline'
]
