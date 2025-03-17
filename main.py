import os
import time
import requests

from tqdm import tqdm #for progress bar

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

# Configure Selenium
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
#chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


def get_data_folder():
    """
    Get the folder where the data files will be saved.
    """
    data_folder = input("Bitte den data Ordner angeben:\n")
    data_folder = data_folder.replace("\\", "/")
    if not os.path.exists(data_folder):
        print("Der angegebene Ordner existiert nicht.\nSollte dieser angelegt werden? [j/n]")
        choice = input().lower()
        if choice == "j":
            os.makedirs(data_folder, exist_ok=True)
    if os.path.exists(data_folder):
        return data_folder
    else:
        return get_data_folder()

def get_website():
    """
    Get the URL of the website to scrape (This was ment for a Patreon collection).
    """
    websiteUrl = input("Bitte die URL der Collection eingeben:\n")
    if not websiteUrl:
        print("Keine eingabe gefunden.\nBitte geben Sie eine URL ein:")
        return get_website()
    else:
        return websiteUrl
    

def get_data():
    """
    Scrapes data file links from a webpage and downloads them.
    """
    driver.get(BASE_URL)
    input("Please login and press Enter to continue...")
    driver.get(BASE_URL)

    wait = WebDriverWait(driver, 120)
    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[data-tag="post-attachment-link"]')))
    except:
        print("Timeout: No attachment links found")
        driver.quit()
        return

    # Extract data file links
    data_links = []
    data_elements = driver.find_elements(By.CSS_SELECTOR, 'a[data-tag="post-attachment-link"]')

    for element in data_elements:
        data_url = element.get_attribute("href")
        data_name = element.text.strip()
        if data_url and data_name.endswith(".data"):
            data_links.append({"url": data_url, "filename": data_name})
            print(f"Found: {data_name} -> {data_url}")

    print(f"Found {len(data_links)} data files in total")
    return data_links

def download_missing_datas(data_links):
    """
    Comparing the data files in the DOWNLOAD_FOLDER with the data_links and download the missing ones.
    """
    # Download missing data files
    existing_datas = os.listdir(DOWNLOAD_FOLDER)
    existing_datas = {f for f in existing_datas if f.endswith(".data")}
    print(f"You allready have downloaded: {len(existing_datas)} datas in this folder.")

    files_to_download = [data_info for data_info in data_links if data_info['filename'] not in existing_datas]

    if not files_to_download:
        print("No new files to download.")
        return

    print(f"We plan on downloading {len(files_to_download)} files.")
    userinput = input("Do you want to continue? [y/n]")
    if userinput.lower() != "y":
        print("Aborting download.")
        return
     
    # Extract cookies from Selenium
    selenium_cookies = driver.get_cookies()
    cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
   
    with tqdm(total=len(files_to_download), desc="Downloading files", unit="file") as progress_bar:
        for data_info in data_links:
            if data_info['filename'] not in existing_datas:
                #print(f"Downloading: {data_info['filename']}")
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

                        #print(f"Downloaded: {data_info['filename']}")
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading {data_info['filename']}: {e}")
                finally:
                    progress_bar.update(1)
    print("Download complete")
    driver.quit()

DOWNLOAD_FOLDER = ""
BASE_URL = ""

if __name__ == "__main__":
    DOWNLOAD_FOLDER = get_data_folder()
    BASE_URL = get_website()
    data_links = get_data()
    download_missing_datas(data_links)
    driver.quit()
