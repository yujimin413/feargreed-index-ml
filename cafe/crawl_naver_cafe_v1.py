from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import pyperclip
import os
from dotenv import load_dotenv

load_dotenv()

NAVER_ID = os.environ.get('NAVER_ID')
NAVER_PW = os.environ.get('NAVER_PW')

# my_id = NAVER_ID
# my_pw = NAVER_PW

# print(f"NAVER_ID: {NAVER_ID}, NAVER_PW: {NAVER_PW}")

# exit()

# Initialize the WebDriver (Chrome in this case)
driver = webdriver.Chrome()  # Make sure chromedriver is in your PATH
driver.get("https://nid.naver.com/nidlogin.login")

try:
    # Wait for the ID input field to be present
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "id")))
    
    # Enter the username
    id_input = driver.find_element(By.ID, "id")
    time.sleep(3)
    pyperclip.copy(NAVER_ID)
    id_input.click()
    id_input.send_keys(Keys.COMMAND+'v')
    
    # Enter the password
    password_input = driver.find_element(By.ID, "pw")
    pyperclip.copy(NAVER_PW)
    time.sleep(3)
    password_input.click()
    password_input.send_keys(Keys.COMMAND+'v')
    
    # Click the Sign in button
    sign_in_button = driver.find_element(By.ID, "log.login")
    sign_in_button.click()
    
    # Wait for a bit to ensure the login process completes
    time.sleep(5)

except TimeoutException:
    print("Loading took too much time!")
finally:
    # Optionally close the browser
    # driver.quit()
    pass

driver.get("https://cafe.naver.com/jaegebal")
time.sleep(10)