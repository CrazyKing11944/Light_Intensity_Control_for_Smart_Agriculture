from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


def open_camera_in_ie_tab(url):
    # Set the path to the ChromeDriver executable
    # You need to download the ChromeDriver executable from https://sites.google.com/chromium.org/driver/
    # and provide the path to its location on your machine.
    driver_path = "path/to/chromedriver.exe"

    # Create a new instance of the Chrome browser
    driver = webdriver.Chrome(executable_path=driver_path)

    try:
        # Open the Chrome browser
        driver.get("chrome://extensions/")

        # Wait for the extensions page to load
        time.sleep(2)

        # Locate the IE Tab extension and click on it
        ie_tab_button = driver.find_element_by_css_selector("div[command='extensions.html.tabs'] button")
        ie_tab_button.click()

        # Wait for the IE Tab extension to open
        time.sleep(2)

        # Open the specified URL in the IE Tab
        driver.get(url)

        # Wait for the page to load (adjust the sleep duration as needed)
        time.sleep(5)

        # You can interact with the page or perform further actions if needed
        # For example, you can capture a screenshot:
        driver.save_screenshot("camera_screenshot.png")

    finally:
        # Close the browser window
        driver.quit()


# Replace 'http://your_camera_url' with the actual URL of your Hikvision camera
camera_url = 'http://your_camera_url'

# Call the function to open the camera view in IE Tab using Chrome
open_camera_in_ie_tab(camera_url)
