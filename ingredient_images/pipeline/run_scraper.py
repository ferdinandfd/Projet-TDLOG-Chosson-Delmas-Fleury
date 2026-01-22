"""
Main script to run the ingredient image scraper.
Orchestrates the entire scraping process from browser setup to image download.
"""

from browser import create_driver
from actions import accept_cookies, search, scroll_down
from downloader import download_images
from config import *

# Initialize browser and navigate to Google Images
driver = create_driver(CHROME_DRIVER_PATH)

# Handle cookie consent and perform search
accept_cookies(driver)
search(driver, QUERY)

# Load more images by scrolling
scroll_down(driver, MAX_SCROLLS)

# Download images to local storage
download_images(
    driver,
    OUTPUT_DIR,
    NB_IMAGES,
    MAX_IMAGE_SIZE
)

# Clean up browser resources
driver.quit()
