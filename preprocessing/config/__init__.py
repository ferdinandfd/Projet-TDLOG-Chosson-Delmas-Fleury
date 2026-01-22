"""
Configuration package for preprocessing pipeline.

Contains settings and ingredient mapping configurations.
"""

from .settings import PreprocessingConfig
from .ingredient_mapping import INGREDIENTS

__all__ = ['PreprocessingConfig', 'INGREDIENTS']
