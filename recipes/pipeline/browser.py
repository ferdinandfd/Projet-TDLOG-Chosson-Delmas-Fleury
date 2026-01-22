"""
Browser automation setup for web scraping.

This module configures Selenium WebDriver with optimized settings for
stable web scraping operations including cookie persistence and French locale.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def create_driver():
    """
    Create and configure Chrome WebDriver for web scraping.
    
    Returns:
        webdriver.Chrome: Configured Chrome driver instance
    """
    options = Options()
    
    # Performance optimizations
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Locale configuration for French recipe site
    options.add_argument("--lang=fr-FR")
    
    # Persistent profile to maintain cookies and login state
    options.add_argument("--user-data-dir=/Users/antoinechosson/selenium_chrome_profile")
    options.add_argument("--profile-directory=Default")

    # Auto-download and setup Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver
