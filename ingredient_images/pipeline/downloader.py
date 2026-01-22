import os
import base64
import requests
from selenium.webdriver.common.by import By

def download_images(driver, output_dir, nb_images, min_size):
    """
    Downloads images from the current page to local storage.
    Handles both data URLs and regular HTTP URLs.
    Filters out images smaller than minimum size to ensure quality.
    Creates output directory if it doesn't exist.
    """
    os.makedirs(output_dir, exist_ok=True)
    images = driver.find_elements(By.TAG_NAME, "img")[:nb_images]

    session = requests.Session()

    for i, img in enumerate(images):
        try:
            src = img.get_attribute("src")
            if not src:
                continue

            filepath = os.path.join(output_dir, f"img_{i}.jpg")

            if src.startswith("data:image"):
                data = base64.b64decode(src.split(",")[1])
                if len(data) < min_size:
                    continue
                with open(filepath, "wb") as f:
                    f.write(data)
            else:
                r = session.get(src, timeout=10)
                content_type = r.headers.get("Content-Type", "")
                if "image" in content_type and len(r.content) > min_size:
                    with open(filepath, "wb") as f:
                        f.write(r.content)

        except Exception as e:
            print(f"Failed image {i}: {e}")
