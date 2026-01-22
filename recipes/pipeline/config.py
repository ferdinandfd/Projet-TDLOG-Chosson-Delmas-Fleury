"""
Configuration parameters for recipe data collection pipeline.

This module defines all configurable parameters for the ML data collection
pipeline including file paths, scraping parameters, and rate limiting settings.
"""

import numpy as np

# Data storage configuration
CSV_PATH = "marmiton_recipes.csv"

# Scraping parameters
PAGES_TO_SCRAPE = np.arange(11, 20, 1)  # Page range for recipe discovery
SCROLL_VALUE = 500  # Pixels to scroll for dynamic content loading
SAVE_EVERY = 5  # Save progress every N processed recipes

# Rate limiting to avoid being blocked
WAIT_BETWEEN_RECIPES = 2  # Seconds to wait between recipe requests
