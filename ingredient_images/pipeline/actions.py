from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

def accept_cookies(driver):
    """
    Handles cookie consent dialog on Google Images.
    Clicks the second button in the dialog which typically accepts cookies.
    Uses a timeout to avoid hanging if dialog doesn't appear.
    """
    try:
        button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH,
                                       '//*[@role="dialog"]//button[2]'))
        )
        button.click()
        time.sleep(1)
    except Exception:
        pass


def search(driver, query):
    """
    Performs a search on Google Images.
    Finds the search textarea, enters the query and submits it.
    Waits for page to load after search submission.
    """
    bar = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.TAG_NAME, "textarea"))
    )
    bar.send_keys(query)
    bar.send_keys(Keys.RETURN)
    time.sleep(2)


def scroll_down(driver, max_scrolls=10):
    """
    Scrolls down the page to load more images.
    Executes multiple scroll actions with random delays to mimic human
    behavior. Random timing helps avoid being detected as a bot.
    """
    for _ in range(max_scrolls):
        script = "window.scrollTo(0, document.body.scrollHeight);"
        driver.execute_script(script)
        time.sleep(random.uniform(2, 4))
