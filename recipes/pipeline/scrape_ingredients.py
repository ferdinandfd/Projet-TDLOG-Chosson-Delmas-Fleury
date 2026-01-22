"""
Recipe ingredient scraping module.

This module handles the extraction of ingredient lists from individual recipe
pages using search functionality and DOM element parsing.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from navigation import accept_cookies, scroll
import time


def get_recipe_ingredients(driver, recipe_name):
    """
    Extract ingredients list for a specific recipe.
    
    Args:
        driver: Selenium WebDriver instance
        recipe_name (str): Name of the recipe to search for
        
    Returns:
        list: List of ingredient names found on recipe page
    """
    ingredients = []

    # Navigate to main site and handle cookies
    driver.get("https://www.marmiton.org/")
    time.sleep(3)
    accept_cookies(driver)

    try:
        # Search for the specific recipe
        search_box = driver.find_element(By.ID, "header__content-search-input")
        search_box.clear()
        search_box.send_keys(recipe_name)
        search_box.send_keys(Keys.RETURN)
    except:
        # Search functionality not available
        return ingredients

    time.sleep(4)  # Allow search results to load

    try:
        # Click on first search result
        first_result = driver.find_element(
            By.XPATH, '//a[contains(@class, "card-content__title")]'
        )
        first_result.click()
        time.sleep(3)
        
        # Scroll to ensure ingredients are loaded
        scroll(driver, 500)

        # Extract ingredient names from recipe page
        elements = driver.find_elements(
            By.XPATH, "//span[contains(@class,'ingredient-name')]"
        )
        for el in elements:
            txt = el.text.strip()
            if txt:
                ingredients.append(txt)
    except:
        # Recipe page not found or ingredients not available
        pass

    return ingredients
