import time
import threading
import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO
import base64
import utils.captcha as captcha
import requests
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO
import base64
import requests
from selenium import webdriver  # Importing webdriver module
from webdriver_manager.chrome import ChromeDriverManager

def create_web_driver():
    options = webdriver.ChromeOptions()
    prefs = {
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
    options.add_argument('--headless')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.implicitly_wait(1)
    return driver

def keep_session_alive(session_id):
    base_url = "https://services.gst.gov.in/services/auth/api/keepalive"

    cookies = {
        'AuthToken': session_id,
    }

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'https://services.gst.gov.in/services/auth/fowelcome',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    while True:
        try:
            response = requests.get(base_url, cookies=cookies, headers=headers)

            if response.status_code == 200:
                if "Your session is expired" in response.text or "You don't have permission" in response.text:
                    print("Session extension failed. Your session is expired or permission issue.")
                else:
                    print("Session extended successfully.")
            else:
                print(f"Failed to extend the session. Status Code: {response.status_code}")

        except Exception as e:
            print(f"Error: {str(e)}")

        time.sleep(30)

def login(username, password):
    max_retries = 10
    retry_count = 0

    while retry_count < max_retries:
        driver = create_web_driver()

        try:
            url = 'https://services.gst.gov.in/services/login?flag=einvoice'
            driver.get(url)
            time.sleep(5)
            
            driver.find_element(By.ID, "username").click()
            driver.find_element(By.ID, "username").clear()
            driver.find_element(By.ID, "username").send_keys(username)

            driver.find_element(By.ID, "user_pass").click()
            driver.find_element(By.ID, "user_pass").clear()
            driver.find_element(By.ID, "user_pass").send_keys(password)

            captcha_image_element = driver.find_element(By.ID, "imgCaptcha")
            captcha_image_data = captcha_image_element.screenshot_as_png

            image = Image.open(BytesIO(captcha_image_data))

            buffer = BytesIO()
            image.save(buffer, format="PNG")
            base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

            captcha_id, captcha_text = captcha.get_captcha_base64(base64_image)

            driver.find_element(By.ID, "captcha").click()
            driver.find_element(By.ID, "captcha").clear()
            driver.find_element(By.ID, "captcha").send_keys(captcha_text)

            button = driver.find_element(By.XPATH, f'//button[text()="Login"]')
            button.click()
            time.sleep(10)

            try:
                alert_element = driver.find_element(By.CLASS_NAME, "alert-danger")
                alert_text = alert_element.text
                print("alert_text", alert_text)

                if 'Invalid Username or Password. Please try again.' in alert_text:
                    return False, 'INVALID'
                elif 'You have entered a wrong password for 3 consecutive times' in alert_text:
                    return False, 'LOCKED'
            except:
                pass

            try:
                alert_success = driver.find_element(By.CLASS_NAME, "alert-success")
                alert_success_text = alert_success.text
                print("alert_success_element", alert_success_text)

                if 'OTP' in alert_success_text:
                    return False, 'OTP'
            except:
                pass

            cookies = driver.get_cookies()
            for cookie in cookies:
                if cookie['name'] == 'AuthToken':
                    auth_token = cookie['value']
                    # print("Login successful. Starting session keep-alive.")
                    # keep_alive_thread = threading.Thread(target=keep_session_alive, args=(auth_token,))
                    # keep_alive_thread.start()
                    return True, auth_token

        except Exception as e:
            retry_count += 1
        finally:
            retry_count += 1
            driver.quit()

    return False, 'PENDING'

def main():
    username = "Shop_30012014"
    password = "Passwords@2"

    max_login_retries = 3
    max_session_retries = 3

    login_successful = False
    session_active = False
    session_id = None

    # Attempt login
    for _ in range(max_login_retries):
        login_successful, auth_token = login(username, password)
        if login_successful:
            session_id = auth_token
            break
        else:
            print("Login failed. Retrying...")
            time.sleep(2)

    if not login_successful:
        print("Failed to login after multiple attempts. Exiting.")
        return

    # Start session keep-alive
    keep_alive_thread = threading.Thread(target=keep_session_alive, args=(session_id,))
    keep_alive_thread.start()

    session_active = True

    # First API
    cookies = {
        'AuthToken': session_id,
        'UserName': 'shop_30012014',
        'EntityRefId': 'T270000275736',
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'https://services.gst.gov.in/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    response_first = requests.get('https://prodcc.gst.gov.in/cchannel/auth/viewnotification', cookies=cookies, headers=headers)

    # Second API
    json_data_second = {
        'fromDate': '2023-10-02',
        'toDate': '2024-04-02',
        'action': 'RR',
        'notifyType': 'S',
    }

    response_second = requests.post(
        'https://prodcc.gst.gov.in/cchannel/auth/api/notifications',
        cookies=cookies,
        headers=headers,
        json=json_data_second,
    )

    # Handle errors in case the response is not in JSON format
    # Extracting notify_ids from the response of the second API
    try:
        response_data = response_second.json()
        notify_ids = [item['notify_id'] for item in response_data.get('data', [])]
    except (KeyError, ValueError) as e:
        print("Error:", e)
        print("Response content:", response_second.content)
        notify_ids = []

    # Third API for each notifyId
    third_responses = []
    for notify_id in notify_ids:
        json_data_third = {
            'notifyId': notify_id,
        }

        response_third = requests.post(
            'https://prodcc.gst.gov.in/cchannel/auth/api/notification',
            headers=headers,
            cookies=cookies,
            json=json_data_third,
        )
        
        # Handle errors in case the response is not in JSON format
        try:
            third_response_json = response_third.json()
        except ValueError as e:
            print(f"Error decoding JSON response from the third API for notifyId {notify_id}: {e}")
            print("Response content:", response_third.content)
            continue
        
        third_responses.append(third_response_json)

    # Now you can process the responses of all APIs
    print("\nResponse of the second API:")
    print(response_second.json())
    print("\nResponses of the third API for each notifyId:")
    for index, response in enumerate(third_responses, start=1):
        print(f"\nResponse {index}:")
        print(response)

    # When finished, ensure to clean up
    keep_alive_thread.join()

    # End the session
    session_active = False
    print("Session ended.")

if __name__ == "__main__":
    main()
