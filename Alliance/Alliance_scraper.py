import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO
import base64
import requests
from webdriver_manager.chrome import ChromeDriverManager
import csv
import os

# Import the captcha module correctly
import utils.captcha as captcha

def create_web_driver():
    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": os.path.join(os.getcwd(), "Output2"),  # Specify the download directory
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "directory_upgrade": True
    }
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--window-size=1920,1400")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--headless')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.implicitly_wait(1)
    return driver

def login(date, pnr):
    max_retries = 10
    retry_count = 0

    while retry_count < max_retries:
        driver = create_web_driver()

        try:
            url = 'https://allianceair.co.in/gst/'
            driver.get(url)
            time.sleep(5)
            
            # Corrected IDs for elements
            driver.find_element(By.ID, "txtDOJ").click()
            driver.find_element(By.ID, "txtDOJ").clear()
            driver.find_element(By.ID, "txtDOJ").send_keys(date)
            time.sleep(3)
            driver.find_element(By.ID, "txtPNR").click()
            driver.find_element(By.ID, "txtPNR").clear()
            driver.find_element(By.ID, "txtPNR").send_keys(pnr)
            time.sleep(3)
            
            captcha_image_element = driver.find_element(By.ID, "Image1")
            captcha_image_data = captcha_image_element.screenshot_as_png

            image = Image.open(BytesIO(captcha_image_data))

            buffer = BytesIO()
            image.save(buffer, format="PNG")
            base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

            captcha_id, captcha_text = captcha.get_captcha_base64(base64_image)
            print("CaptchaEarlier----------", captcha_text)
            time.sleep(2)
            captcha_text_cap = captcha_text.upper()  # Capitalize all characters
            print("Captcha----------", captcha_text_cap)

            driver.find_element(By.ID, "txtVerificationCodeNew").click()
            driver.find_element(By.ID, "txtVerificationCodeNew").clear()
            driver.find_element(By.ID, "txtVerificationCodeNew").send_keys(captcha_text)
            button = driver.find_element(By.XPATH, f'//*[@id="btnSearch"]')
            button.click()
            time.sleep(15)

            try:
                driver.find_element(By.ID, "lnkdownload").click()
                print("Files downloaded")
            except:
                print("Files not downloaded")
                try:
                    # Check if an alert pop-up is present
                    alert = driver.switch_to.alert
                    alert_text = alert.text
                    print("Alert Text:", alert_text)
                    # Write the PNR to a CSV file named "failed"
                    with open("failed.csv", "a") as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(["Invalid captcha", pnr, date, alert_text])
                    alert.accept()  # Close the alert
                except:
                    # Write the PNR to a CSV file named "failed"
                    with open("failed.csv", "a") as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(["Failed to download", pnr, date])

            time.sleep(5)
            
            # Extract authentication token from cookies
            auth_token = None
            cookies = driver.get_cookies()
            for cookie in cookies:
                if cookie['name'] == 'AuthToken':
                    auth_token = cookie['value']
                    break

            driver.quit()  # Close the browser after successful login
            return auth_token

        except Exception as e:
            print("Error:", e)
            retry_count += 1
            driver.quit()

    return None
    
def main():
    # Update with the path to your CSV file
    csv_file_path = "/Users/finkraft/dev/AirIndia_scrapers/scrapers/Alliance/Alliance Air_dec2023.csv"

    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            date = row['Date']
            pnr = row['PNR']
            
            print(f"Processing PNR: {pnr}, Date: {date}")

            auth_token = login(date, pnr)

if __name__ == "__main__":
    main()


