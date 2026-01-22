"""
Recipe data collection pipeline for ML recommender system.

This module orchestrates the complete data collection process by:
1. Loading existing recipe data
2. Scraping new recipe titles from recipe website
3. Collecting ingredient lists for recipes
4. Persisting data incrementally to prevent data loss
"""

from browser import create_driver
from scrape_recipes import scrape_recipe_titles
from scrape_ingredients import get_recipe_ingredients
from persistence import load_dataset, save_dataset
from config import *
import time

# Initialize browser driver with custom configuration
driver = create_driver()

# Load existing dataset to avoid duplicate scraping
df = load_dataset(CSV_PATH)
existing_recipes = df["recipe_title"].tolist()

# Scrape new recipe titles from configured pages
new_recipes = scrape_recipe_titles(
    driver,
    PAGES_TO_SCRAPE,
    SCROLL_VALUE,
    existing_recipes
)

# Add new recipes to dataset with empty ingredient lists
for recipe in new_recipes:
    df.loc[len(df)] = [recipe, []]

# Identify recipes that need ingredient scraping
recipes_to_process = df[df["ingredients"].apply(len) == 0]["recipe_title"].tolist()

# Scrape ingredients for each recipe with progress tracking
for i, recipe in enumerate(recipes_to_process):
    ingredients = get_recipe_ingredients(driver, recipe)
    df.loc[df["recipe_title"] == recipe, "ingredients"] = [ingredients]

    # Save progress periodically to prevent data loss
    if (i + 1) % SAVE_EVERY == 0:
        save_dataset(df, CSV_PATH)

    # Rate limiting to avoid being blocked
    time.sleep(WAIT_BETWEEN_RECIPES)

# Final save and cleanup
save_dataset(df, CSV_PATH)
driver.quit()
