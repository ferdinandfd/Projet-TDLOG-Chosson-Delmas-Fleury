"""
Web navigation utilities for recipe scraping.

This module provides helper functions for common web navigation tasks
including cookie consent handling and dynamic content loading through scrolling.
"""

from selenium.webdriver.common.by import By
import time


def accept_cookies(driver):
    """
    Accept cookie consent dialog if present.
    
    Args:
        driver: Selenium WebDriver instance
    """
    try:
        btn = driver.find_element(By.ID, "didomi-notice-agree-button")
        btn.click()
        time.sleep(2)  # Allow time for dialog to close
    except:
        # Cookie dialog not found or already accepted
        pass


def scroll(driver, value, n=20):
    """
    Scroll page to load dynamic content.
    
    Args:
        driver: Selenium WebDriver instance
        value (int): Pixels to scroll per iteration
        n (int): Number of scroll iterations
    """
    for _ in range(n):
        driver.execute_script(f"window.scrollBy(0, {value})")
        time.sleep(0.1)  # Small delay between scrolls
