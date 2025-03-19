import os
import time
import requests
from getpass import getpass

#dependencies
from tqdm import tqdm #for progress bar
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

"""
TODO:
- Add dynamic input for the get_data CSS_SELECTOR
- Add dynamic input for file extension

Ask chatgpt:
- What are best practices for github the read me file?
- What is the MIT Licence?
- How to make a good README file?
"""

def get_user_input():
    """
    Fill the variabals DOWNLOAD_FOLDER and BASE_URL.
    Either from a user_input.txt file or by asking the user.
    """
    #is there an existing user_input.txt file
    print("Checking for user_input.txt file")
    if os.path.exists("user_input.txt"):
        print("Found input from a past seassion")
        user_input = input("Do you want to use the past input? [y/n]:\n")
        if user_input.lower() == "y" or user_input.lower() == "j":
            with open("user_input.txt", "r") as f:
                for line in f:
                    if line.startswith("DOWNLOAD_FOLDER"):
                        DOWNLOAD_FOLDER = line.split("=")[1].strip()
                    elif line.startswith("BASE_URL"):
                        BASE_URL = line.split("=")[1].strip()
                    elif line.startswith("LOGIN_URL"):
                        LOGIN_URL = line.split("=")[1].strip()
            return DOWNLOAD_FOLDER, BASE_URL, LOGIN_URL
    
    #get user input
    DOWNLOAD_FOLDER = get_download_folder()
    BASE_URL, LOGIN_URL = get_website()
    
    return DOWNLOAD_FOLDER, BASE_URL, LOGIN_URL


def get_download_folder():
    """
    Get the folder where the data files will be saved.
    """
    if DOWNLOAD_FOLDER != "":
        print(f"Last folder: {DOWNLOAD_FOLDER}\n")
    data_folder = input("What is the Download Folder?:\n")

    data_folder = data_folder.replace("\\", "/")
    if not os.path.exists(data_folder):
        user_input = input("The given folder does not exist, should I create the folder? [y/n]:\n")
        if user_input.lower() == "y" or user_input.lower() == "j":
            os.makedirs(data_folder, exist_ok=True)

    if os.path.exists(data_folder):
        print(f"Downloading to: {data_folder}")
        return data_folder
    else:
        return get_download_folder()

def get_website():
    """
    Get the URL of the website to scrape (This was ment for a Patreon collection).
    """
    if BASE_URL != "":
        print(f"Last URL: {BASE_URL}\n")
    websiteUrl = input("The URL of the Collection:\n")
    if websiteUrl:
        print(f"Scraping: {websiteUrl}")
    else:
        print("No input found.")
        return get_website()


    if LOGIN_URL != "":
        print(f"Last URL: {LOGIN_URL}\n")    
    loginUrl = input("The URL of the Login page:\n")
    if loginUrl:
        print(f"Login on: {loginUrl}")
    else:
        print("No input found.")
        return get_website()

    return websiteUrl, loginUrl
    

def get_login_data():
    load_dotenv()    
    MAIL = os.getenv('MAIL')
    PASSWORD = os.getenv('PASSWORD')
    if not MAIL or not PASSWORD:
        print("No login data found in .env file")
        user_input = input("Do you want to create a new .env file? [y/n]:\n")
        if user_input.lower() == "y" or user_input.lower() == "j":
            MAIL = input("Mail: ")
            PASSWORD = getpass()

            with open(".env", "w") as f:
                f.write(f"MAIL={MAIL}\n")
                f.write(f"PASSWORD={PASSWORD}\n")
            print("Created .env file")
            return MAIL, PASSWORD
        else:
            print("When the Browser opens you will need to login manualy")
            return
    else:
        print("Login data found in .env file")
        # Runing the skript in headless mode
        return MAIL, PASSWORD

def login(driver):
    #start the webdriver
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 20)

    #commented out since this did not work just now...
    try:
        #wait for the login form to load
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="email"]')))
        email = driver.find_element(By.CSS_SELECTOR, 'input[name="email"]')
        email.click()
        email.send_keys(MAIL)
        
        continue_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        continue_button.click()
        time.sleep(5)

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="current-password"]')))
        password = driver.find_element(By.CSS_SELECTOR, 'input[name="current-password"]')
        password.click()
        password.send_keys(PASSWORD)
        time.sleep(5)

        continue_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        continue_button.click()
        time.sleep(5)
    except:
        print("Error: Could not login")
        driver.quit()
        exit()
    #wait for the login to complete
    time.sleep(5)
    print("Login complete")

def get_links_to_download(driver):
    """
    Scrapes data file links from a webpage and downloads them.
    """
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 120)
    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[data-tag="post-attachment-link"]')))
    except:
        print("Timeout: No attachment links found")
        driver.quit()
        exit()

    # Extract data file links
    data_links = []
    data_elements = driver.find_elements(By.CSS_SELECTOR, 'a[data-tag="post-attachment-link"]')

    for element in data_elements:
        data_url = element.get_attribute("href")
        data_name = element.text.strip()
        if data_url and data_name.endswith(".zip"):
            data_links.append({"url": data_url, "filename": data_name})
            print(f"Found: {data_name} -> {data_url}")

    print(f"Found {len(data_links)} data files in total")
    return data_links

def download_missing_datas(driver, data_links):
    """
    Comparing the data files in the DOWNLOAD_FOLDER with the data_links and download the missing ones.
    """
    # Download missing data files
    existing_datas = os.listdir(DOWNLOAD_FOLDER)
    existing_datas = {f for f in existing_datas if f.endswith(".zip")}
    print(f"You allready have downloaded: {len(existing_datas)} files in this folder.")

    files_to_download = []
    for data_info in data_links:
        if data_info['filename'] not in existing_datas and data_info['filename'] not in files_to_download:
            files_to_download.append(data_info)

    if not files_to_download:
        print("No new files to download.")
        return

    print(f"We plan on downloading {len(files_to_download)} files.")
    user_input = input("Do you want to continue? [y/n]:\n")
    if user_input.lower() != "y" and user_input.lower() != "j":
        print("Aborting download.")
        return
     
    # Extract cookies from Selenium
    selenium_cookies = driver.get_cookies()
    cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
   
    with tqdm(total=len(files_to_download), desc="Downloading files", unit="file") as progress_bar:
        for data_info in data_links:
            if data_info['filename'] not in existing_datas:
                print(f"\nDownloading: {data_info['filename']}")
                try:
                    # Use cookies in the requests session
                    with requests.Session() as session:
                        session.cookies.update(cookies)
                        response = session.get(data_info['url'], stream=True)
                        response.raise_for_status()

                        # Save the file to the DOWNLOAD_FOLDER
                        file_path = os.path.join(DOWNLOAD_FOLDER, data_info['filename'])
                        with open(file_path, 'wb') as file:
                            for chunk in response.iter_content(chunk_size=8192):
                                file.write(chunk)

                except requests.exceptions.RequestException as e:
                    print(f"Error downloading {data_info['filename']}: {e}")
                finally:
                    progress_bar.update(1)
                    #reduce load on the system and server
                    time.sleep(2)
    print("Download complete")

def remember_user_input():
    """
    Saves the user input DOWNLOAD_FOLDER and BASE_URL to a .txt file.
    """
    with open("user_input.txt", "w") as f:
        f.write(f"DOWNLOAD_FOLDER={DOWNLOAD_FOLDER}\n")
        f.write(f"BASE_URL={BASE_URL}\n")
        f.write(f"LOGIN_URL={LOGIN_URL}\n")
    print("Saved user input to user_input.txt")


def configure_driver(headless=True):
    """
    Configure the Selenium webdriver.
    """
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    if headless:
        chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Bypass WebDriver detection
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        })
        """
    })

    return driver

DOWNLOAD_FOLDER = ""
LOGIN_URL = ""
BASE_URL = ""
MAIL = ""
PASSWORD = ""

if __name__ == "__main__":
    DOWNLOAD_FOLDER, BASE_URL, LOGIN_URL = get_user_input()
    

    MAIL, PASSWORD = get_login_data()
    remember_user_input()

    if MAIL and PASSWORD:
        driver = configure_driver(headless=True)
    else:
        driver = configure_driver(headless=False)
    login(driver)

    data_links = get_links_to_download(driver)
    if data_links:
        download_missing_datas(driver, data_links)
    driver.quit()

