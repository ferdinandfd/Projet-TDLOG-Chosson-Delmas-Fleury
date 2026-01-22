"""
Configuration file for ingredient image scraper.
Modify by hand the values to change target ingredient.
"""

INGREDIENT = "pomme_de_terre"
QUERY = "photo pomme de terre"
NB_IMAGES = 2000
MAX_IMAGE_SIZE = 1024
MAX_SCROLLS = 10

CHROME_DRIVER_PATH = "/usr/local/bin/chromedriver"
OUTPUT_DIR = f"data/ingredient_images/{INGREDIENT}"
