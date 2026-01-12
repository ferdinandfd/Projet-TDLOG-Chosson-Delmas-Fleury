from selenium_functions import *

# Start the browser using Service
service = Service(executable_path='/usr/local/bin/chromedriver')
driver = webdriver.Chrome(service=service)
driver.get("https://images.google.com/")
time.sleep(2)

#waits until cookie accpetance tab opens and then accepts it if it appears
wait_accept_cookies(driver)

ingredient = "photo pomme de terre"

send_in_search_bar(driver, ingredient)

scroll_down(driver, max_scrolls = 10)



# Create a 'scraper' folder in the working directory if it doesn't exist
scraper_dir = os.path.join(os.getcwd(), ingredient+"_images")
os.makedirs(scraper_dir, exist_ok=True)

# Find and download the first 100 images
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "img"))
    )
    download_pictures(driver, nb_images=2000, max_size=1024, output_directory=scraper_dir, query = ingredient)

except Exception as e:
    print("FAILED TO FIND IMAGES:", e)

print("\nSearch and download completed!")
input("Press Enter to close the browser...")
driver.quit()
