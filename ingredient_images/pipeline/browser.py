from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def create_driver(chromedriver_path):
    """
    Creates and configures a Chrome WebDriver instance.
    Automatically navigates to Google Images homepage.
    Returns the configured driver for use in scraping.
    """
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service)
    driver.get("https://images.google.com/")
    return driver
