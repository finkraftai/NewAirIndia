import imaplib
import time
import requests
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import traceback


def _web_driver():
    # download_dir = "C:/Users/annav/Desktop/NewAirIndia/pdfs/"  # Replace with the actual path to your download directory
    options = webdriver.ChromeOptions()
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "directory_upgrade": True,
        # "download.default_directory": download_dir,  # Set the default download directory
        # "download.prompt_for_download": False,
        # "plugins.always_open_pdf_externally": True  # Ensure PDFs are downloaded rather than opened
    }
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--window-size=1920,1400")
    options.add_argument('--disable-gpu')
    # options.add_argument('--headless')  # Uncomment for headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.implicitly_wait(10)
    return driver

def login(driver, email, password):
    try:
        print("-" * 20 + ' INITIATING LOGIN ' + "-" * 20)
        driver.get('https://gst.airindia.com/portal/index.html')
        driver.save_screenshot('login.png')
        driver.delete_all_cookies()
        driver.execute_script('window.localStorage.clear()')
        driver.execute_script('window.sessionStorage.clear()')
        time.sleep(4)
        
        # Wait for the email input field to be present
        print("Waiting for email input field to be present...")
        email_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='container-airindiagst---Login--inp-loginEmail-inner']"))
        )
        print("Email input field found")
        # Enter email
        print("Entering email...")
        email_field.send_keys(email)
        # Enter password
        password_field = driver.find_element(By.XPATH, "//*[@id='container-airindiagst---Login--inp-loginPass-inner']")
        password_field.send_keys(password)
        # Click login button
        login_button = driver.find_element(By.XPATH, "//*[@id='container-airindiagst---Login--idLoginButton-BDI-content']")
        login_button.click()
        print("Login Clicked")
        # Wait for the page to load after login
        time.sleep(5)
        # Now, you can perform actions on the portal page after login
        driver.save_screenshot('loggedin.png')

        # try:
        #     driver.find_element(By.ID, 'sessionConfirmAlertForm_sessionYesButton').click()
        #     print("Another Session Found and Killed")
        #     time.sleep(30)
        #     print("Trying Relogin")
        # except:
        #     print("No Other Session Found")
        #     pass

        max_retries = 5  # Maximum number of OTP retrieval retries
        while max_retries > 0:
            try:
                otp = input("Enter OTP:")
                driver.find_element(By.XPATH, "//*[@id='container-airindiagst---Login--inp-verifyOtp-inner']").send_keys(otp)
                driver.find_element(By.XPATH, "//*[@id='container-airindiagst---Login--btn-verifyOtp-inner']").click()
                print("OTP Submitted")
                driver.save_screenshot('otp_submitted.png')
                time.sleep(2)
                driver.find_element(By.XPATH, "//*[@id='__mbox-btn-1-inner']").click()
                time.sleep(5)
                # cookie = driver.get_cookies()
                break  # Break out of the loop if OTP submission is successful
            except Exception as e:
                print("OTP Error:", str(e))
                max_retries -= 1
                if max_retries == 0:
                    return ('error', 'otp error')
                else:
                    print(f"Retrying... {max_retries} retries left")
                    time.sleep(2)  # Add a small delay before retrying

    except Exception as e:
        print(f"An error occurred during login: {e}")
        traceback.print_exc()

def gst_Dashboard(driver):
    try:
        driver.get('https://gst.airindia.com/portal/index.html#/LandingPage')
        print("dashboard opened")
        time.sleep(5)
        driver.save_screenshot('dashboard.png')  # Screenshot for debugging

        driver.find_element(By.XPATH, "//*[@id='container-airindiagst---LandingPage--priorTO']").click()
        print("Clicked priorTO link")
        time.sleep(5)
        driver.save_screenshot('priorTO.png')

        element = driver.find_element(By.XPATH, "//*[@id='container-airindiagst---DocumentHistoryPriorTo--title-inner']")

        # Extract the text from the element
        total_count_text = element.text

        # Extract the number from the text
        total_count = int(total_count_text.split('(')[1].split(' ')[-1][:-1])

        print("Total count:", total_count)

        # Calculate the number of loops required
        items_per_page = 100  # Adjust if different
        count_loop = (total_count // items_per_page) + (1 if total_count % items_per_page > 0 else 0)

        print("Number of loops needed:", count_loop)

        # Loop to click the "More" button
        for _ in range(count_loop):
            try:
                # Find and click the "More" button
                more_button = driver.find_element(By.XPATH, "//*[@id='container-airindiagst---DocumentHistoryPriorTo--morelink']")  # Replace with actual XPath of the "More" button
                more_button.click()
                time.sleep(2)  # Adjust sleep time as necessary to allow content to load
            except Exception as e:
                print(f"An error occurred: {e}")
                break  # Exit the loop if there's an error

        # Find and click the "Select All" checkbox
        select_all_checkbox = driver.find_element(By.XPATH, "//*[@id='container-airindiagst---DocumentHistoryPriorTo--tbl_gstInvoices-selall']/div")  # Replace with actual XPath of the "Select All" checkbox
        select_all_checkbox.click()
        time.sleep(3)

        download_btn = driver.find_element(By.XPATH, "//*[@id='container-airindiagst---DocumentHistoryPriorTo--btn-excel-inner']")  # Replace with actual XPath of the "Download" button
        download_btn.click()
        time.sleep(10)

        # Find and click the "Download" button
        download_btn = driver.find_element(By.XPATH, "//*[@id='container-airindiagst---DocumentHistoryPriorTo--btn-pdf-inner']")  # Replace with actual XPath of the "Download" button
        download_btn.click()

        # Handle the popup and click the "Yes" button
        try:
            # Wait for the "Yes" button in the popup to be present
            time.sleep(2)  # Adjust this sleep time as necessary
            yes_button = driver.find_element(By.XPATH, "//*[@id='__mbox-btn-2']")  # Replace with the actual XPath of the "Yes" button
            yes_button.click()
        except Exception as e:
            print(f"An error occurred while trying to click the 'Yes' button: {e}")

        time.sleep(250)
        driver.quit()


    except Exception as e:
        print(f"An error occurred while extracting rows from the table: {e}")
        traceback.print_exc()

# Example usage:
def main():
    driver = _web_driver()
    login(driver,"gst.shell@in.fcm.travel","FCMindia@123")
    gst_Dashboard(driver)

if __name__ == "__main__":
    main()
