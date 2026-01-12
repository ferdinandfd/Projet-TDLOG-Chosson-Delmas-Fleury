from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import requests
import base64
import random


# Handle cookie consent popup if it appears
def wait_accept_cookies(driver):
    try:
        bouton_accepter = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div[2]/div[3]/span/div/div/div/div[3]/div[1]/button[2]'))
        )
        bouton_accepter.click()
        driver.switch_to.default_content()
        time.sleep(1)
    except:
        print("FAILED TO ACCEPT COOKIES")
        pass


# Locate the search bar and type a query
def send_in_search_bar(driver, query):
    try:
        barre_recherche = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[4]/form/div[1]/div[1]/div[1]/div[1]/div[2]/textarea'))
        )
        barre_recherche.send_keys(query)
        barre_recherche.send_keys(Keys.RETURN)
        time.sleep(2)
    except Exception as e:
        print("FAILED TO CLICK SEARCH BAR OR TYPE QUERY:", e)


# Scroll to load more images (version plus naturelle)
import random
import time
#    Scrolle progressivement vers le bas de la page.

def scroll_down(driver, max_scrolls=10):


    for _ in range(max_scrolls):
        current_scroll_height = driver.execute_script("return window.pageYOffset;")
        bottom_scroll_height = driver.execute_script("return document.body.scrollHeight")

        n = random.randint(1,4)
        for k in range(1,n):
            scroll_pos = ( (n-k)*current_scroll_height + k*bottom_scroll_height )/n
            driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
            time.sleep(random.uniform(1, 2))
        
        
        time.sleep(random.uniform(3, 5))



def download_pictures(driver, nb_images, max_size, output_directory, query):
    img_elements = driver.find_elements(By.TAG_NAME, "img")[:nb_images]
    session = requests.Session()
    for i, img_element in enumerate(img_elements):
        print(f"\nWorking on downloading image: {i}")
        try:
            img_url = img_element.get_attribute('src')
            if not img_url:
                print(f"Image {i+1} has no src attribute, skipping...")
                continue

            if img_url.startswith('data:image'):
                base64_data = img_url.split(',')[1]
                image_data = base64.b64decode(base64_data)
                if len(image_data) < max_size:
                    print(f"Image {i+1} is smaller than 1KB, skipping...")
                    continue
                filename =  query + f"{i}.jpg"
                filepath = os.path.join(output_directory, filename)
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                print(f"Base64 image {i+1} saved as {filepath}")

            else:
                if not img_url.startswith(('http://', 'https://')):
                    print(f"Image {i+1} has an invalid URL, skipping...")
                    continue
                response = session.get(img_url, stream=True, timeout=10, allow_redirects=True)
                if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
                    image_data = response.content
                    if len(image_data) < max_size:
                        print(f"Image {i+1} is smaller than 1KB, skipping...")
                        continue
                    filename = filename =  query + f"{i}.jpg"
                    filepath = os.path.join(output_directory, filename)
                    with open(filepath, 'wb') as f:
                        f.write(image_data)
                    print(f"Image {i+1} downloaded as {filepath}")
                else:
                    print(f"Failed to download image {i+1}: HTTP {response.status_code} or not an image")
        except Exception as e:
            print(f"Failed to download image {i+1}: {e}")

    print(f"Found {len(img_elements)} image elements on page")