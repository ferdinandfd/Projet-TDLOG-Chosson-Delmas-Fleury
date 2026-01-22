"""
Preprocessing Pipeline Runner

This module orchestrates the complete data preprocessing pipeline for the
Recipe Recommender system. It coordinates the matrix creation, cleaning,
and recipe filtering steps to produce clean, consistent datasets.

Pipeline Steps:
1. Create recipe-ingredient binary matrix from raw recipe data
2. Clean and standardize the matrix using ingredient mapping
3. Filter recipe dataset to match the cleaned matrix dimensions
4. Generate comprehensive reports on the preprocessing results

Usage:
    python -m preprocessing.src.pipeline_runner
"""

import logging
import time
from pathlib import Path

from ..config.settings import PreprocessingConfig
from .matrix_creator import MatrixCreator
from .matrix_cleaner import MatrixCleaner
from .recipe_filter import RecipeFilter

logger = logging.getLogger(__name__)


class PreprocessingPipeline:
    """
    Main preprocessing pipeline coordinator.
    
    This class manages the complete preprocessing workflow,
    ensuring all steps are executed in the correct order and
    maintaining consistency across all operations.
    """
    
    def __init__(self, config: PreprocessingConfig = None):
        """
        Initialize the preprocessing pipeline.
        
        Args:
            config: Optional preprocessing configuration
        """
        self.config = config or PreprocessingConfig()
        self.matrix_creator = MatrixCreator(self.config)
        self.matrix_cleaner = MatrixCleaner(self.config)
        self.recipe_filter = RecipeFilter(self.config)
        self.pipeline_report = {}
        
    def setup_output_directories(self) -> None:
        """Create all necessary output directories."""
        logger.info("Setting up output directories")
        
        directories = [
            Path(self.config.RAW_MATRIX_PATH).parent,
            Path(self.config.CLEANED_MATRIX_PATH).parent,
            Path(self.config.FILTERED_RECIPES_PATH).parent,
            Path(self.config.OUTPUT_DIR)
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {directory}")
    
    def step_1_create_matrix(self) -> bool:
        """
        Step 1: Create recipe-ingredient binary matrix.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=" * 50)
        logger.info("STEP 1: Creating Recipe-Ingredient Matrix")
        logger.info("=" * 50)
        
        try:
            start_time = time.time()
            
            # Create the binary matrix
            matrix = self.matrix_creator.run_full_pipeline()
            
            # Collect statistics
            stats = self.matrix_creator.get_matrix_statistics()
            
            elapsed_time = time.time() - start_time
            
            self.pipeline_report['step_1_matrix_creation'] = {
                'status': 'success',
                'elapsed_time': elapsed_time,
                'matrix_shape': matrix.shape,
                'statistics': stats
            }
            
            msg = f"Step 1 completed successfully in {elapsed_time:.2f}s"
            logger.info(msg)
            return True
            
        except Exception as e:
            logger.error(f"Step 1 failed: {e}")
            self.pipeline_report['step_1_matrix_creation'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    def step_2_clean_matrix(self) -> bool:
        """
        Step 2: Clean and standardize the ingredient matrix.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=" * 50)
        logger.info("STEP 2: Cleaning and Standardizing Matrix")
        logger.info("=" * 50)
        
        try:
            start_time = time.time()
            
            # Clean the matrix
            cleaned_matrix = self.matrix_cleaner.run_full_pipeline()
            
            # Collect cleaning report
            cleaning_report = self.matrix_cleaner.get_cleaning_report()
            
            elapsed_time = time.time() - start_time
            
            self.pipeline_report['step_2_matrix_cleaning'] = {
                'status': 'success',
                'elapsed_time': elapsed_time,
                'cleaned_matrix_shape': cleaned_matrix.shape,
                'cleaning_report': cleaning_report
            }
            
            msg = f"Step 2 completed successfully in {elapsed_time:.2f}s"
            logger.info(msg)
            return True
            
        except Exception as e:
            logger.error(f"Step 2 failed: {e}")
            self.pipeline_report['step_2_matrix_cleaning'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    def step_3_filter_recipes(self) -> bool:
        """
        Step 3: Filter recipe dataset to match cleaned matrix.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=" * 50)
        logger.info("STEP 3: Filtering Recipe Dataset")
        logger.info("=" * 50)
        
        try:
            start_time = time.time()
            
            # Filter recipes
            filtered_recipes = self.recipe_filter.run_full_pipeline()
            
            # Collect filtering report
            filtering_report = self.recipe_filter.get_filtering_report()
            
            elapsed_time = time.time() - start_time
            
            self.pipeline_report['step_3_recipe_filtering'] = {
                'status': 'success',
                'elapsed_time': elapsed_time,
                'filtered_recipes_shape': filtered_recipes.shape,
                'filtering_report': filtering_report
            }
            
            msg = f"Step 3 completed successfully in {elapsed_time:.2f}s"
            logger.info(msg)
            return True
            
        except Exception as e:
            logger.error(f"Step 3 failed: {e}")
            self.pipeline_report['step_3_recipe_filtering'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    def validate_final_outputs(self) -> bool:
        """
        Validate that all pipeline outputs are consistent.
        
        Returns:
            True if validation passes, False otherwise
        """
        logger.info("=" * 50)
        logger.info("FINAL VALIDATION")
        logger.info("=" * 50)
        
        try:
            # Check if all files exist
            required_files = [
                self.config.RAW_MATRIX_PATH,
                self.config.CLEANED_MATRIX_PATH,
                self.config.FILTERED_RECIPES_PATH
            ]
            
            for file_path in required_files:
                if not Path(file_path).exists():
                    logger.error(f"Required file missing: {file_path}")
                    return False
            
            # Load and validate dimensions
            import pandas as pd
            
            cleaned_matrix = pd.read_csv(self.config.CLEANED_MATRIX_PATH)
            filtered_recipes = pd.read_csv(self.config.FILTERED_RECIPES_PATH)
            
            if len(cleaned_matrix) != len(filtered_recipes):
                logger.error(
                    f"Dimension mismatch: matrix has {len(cleaned_matrix)} "
                    f"rows, recipes has {len(filtered_recipes)} rows"
                )
                return False
            
            logger.info("Final validation passed")
            self.pipeline_report['final_validation'] = {
                'status': 'success',
                'matrix_rows': len(cleaned_matrix),
                'matrix_columns': len(cleaned_matrix.columns),
                'recipe_rows': len(filtered_recipes),
                'recipe_columns': len(filtered_recipes.columns)
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Final validation failed: {e}")
            self.pipeline_report['final_validation'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    def save_pipeline_report(self) -> None:
        """Save the complete pipeline report."""
        import json
        
        report_path = Path(self.config.OUTPUT_DIR) / "pipeline_report.json"
        
        logger.info(f"Saving pipeline report to {report_path}")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.pipeline_report, f, indent=2, default=str)
        
        logger.info("Pipeline report saved")
    
    def run_complete_pipeline(self) -> bool:
        """
        Run the complete preprocessing pipeline.
        
        Returns:
            True if all steps successful, False otherwise
        """
        pipeline_start_time = time.time()
        
        logger.info("🚀 Starting Recipe Preprocessing Pipeline")
        logger.info(f"Configuration: {self.config}")
        
        # Setup directories
        self.setup_output_directories()
        
        # Initialize pipeline report
        self.pipeline_report = {
            'pipeline_start_time': time.time(),
            'config': {
                'raw_recipes_path': str(self.config.RAW_RECIPES_PATH),
                'raw_matrix_path': str(self.config.RAW_MATRIX_PATH),
                'cleaned_matrix_path': str(self.config.CLEANED_MATRIX_PATH),
                'filtered_recipes_path': str(self.config.FILTERED_RECIPES_PATH)
            }
        }
        
        # Run pipeline steps
        success = True
        
        if success:
            success = self.step_1_create_matrix()
        
        if success:
            success = self.step_2_clean_matrix()
        
        if success:
            success = self.step_3_filter_recipes()
        
        if success:
            success = self.validate_final_outputs()
        
        # Complete pipeline report
        pipeline_end_time = time.time()
        total_elapsed = pipeline_end_time - pipeline_start_time
        
        self.pipeline_report['pipeline_end_time'] = pipeline_end_time
        self.pipeline_report['total_elapsed_time'] = total_elapsed
        self.pipeline_report['overall_status'] = (
            'success' if success else 'failed'
        )
        
        # Save report
        self.save_pipeline_report()
        
        # Final message
        if success:
            logger.info("🎉 Pipeline completed successfully!")
            logger.info(f"⏱️  Total time: {total_elapsed:.2f} seconds")
            logger.info(f"📊 Report saved to: {self.config.OUTPUT_DIR}")
        else:
            logger.error("❌ Pipeline failed!")
        
        return success


def run_preprocessing_pipeline(config: PreprocessingConfig = None) -> bool:
    """
    Convenience function to run the complete preprocessing pipeline.
    
    Args:
        config: Optional preprocessing configuration
        
    Returns:
        True if successful, False otherwise
    """
    pipeline = PreprocessingPipeline(config)
    return pipeline.run_complete_pipeline()


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('preprocessing.log')
        ]
    )
    
    # Run pipeline
    config = PreprocessingConfig()
    success = run_preprocessing_pipeline(config)
    
    exit(0 if success else 1)
