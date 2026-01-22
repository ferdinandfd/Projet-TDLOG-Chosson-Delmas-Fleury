"""
Recipe title scraping module.

This module handles the collection of recipe titles from recipe listing pages,
implementing deduplication logic to avoid scraping existing recipes.
"""

from selenium.webdriver.common.by import By
from navigation import accept_cookies, scroll
import time


def scrape_recipe_titles(driver, pages, scroll_value, existing_recipes):
    """
    Scrape recipe titles from multiple recipe listing pages.
    
    Args:
        driver: Selenium WebDriver instance
        pages (iterable): Page numbers to scrape
        scroll_value (int): Pixels to scroll for loading dynamic content
        existing_recipes (list): List of already scraped recipe titles
        
    Returns:
        list: New recipe titles not in existing_recipes
    """
    new_recipes = []

    for page in pages:
        # Navigate to recipe listing page
        url = f"https://www.marmiton.org/recettes/index/categorie/plat-principal/{page}"
        driver.get(url)
        time.sleep(2)  # Allow page to load

        # Handle cookie consent
        accept_cookies(driver)
        
        # Scroll to load dynamic content
        scroll(driver, scroll_value)

        # Extract recipe titles from page
        titles = driver.find_elements(By.XPATH, '//a[contains(@class, "card-content__title")]')
        for t in titles:
            name = t.text.strip()
            # Add title if not empty and not already collected
            if name and name not in existing_recipes and name not in new_recipes:
                new_recipes.append(name)

    return new_recipes
