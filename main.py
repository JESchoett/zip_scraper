from playwright.sync_api import sync_playwright
import os
import time
from urllib.parse import urljoin

def get_zip_folder():
    zip_folder = input("Bitte den zip Ordner angeben:\n")
    zip_folder = zip_folder.replace("\\", "/")
    if not os.path.exists(zip_folder):
        print("Der angegebene Ordner existiert nicht.\nSollte dieser angelegt werden? [j/n]")
        choice = input().lower()
        if choice == "j":
            os.makedirs(zip_folder, exist_ok=True)
    if os.path.exists(zip_folder):
        return zip_folder
    else:
        return get_zip_folder()

def get_website():
    websiteUrl = input("Bitte die URL der Collection eingeben:\n")
    if not websiteUrl:
        print("Keine eingabe gefunden.\nBitte geben Sie eine URL ein:")
        return get_website()
    else:
        return websiteUrl
    
def get_browser():
    print(f"Meine exe ist: {BROWSER_PATH}")
    browser_path = input("Bitte den Pfad zum Browser (zur exe) angeben:\n")
    browser_path = browser_path.replace("\\", "/")
    
    if os.path.isfile(browser_path) and browser_path.endswith(".exe"):
        return browser_path
    
    # Check if the path is a directory
    elif os.path.isdir(browser_path):
        # Look for an .exe file in the directory
        for file in os.listdir(browser_path):
            if file.endswith(".exe"):  # Adjust for other browser names if needed
                return os.path.join(browser_path, file).replace("\\", "/")
    
    # If no valid .exe is found
    print("Der angegebene Pfad ist nicht korrekt oder enthält keine .exe-Datei.\nBitte geben Sie den korrekten Pfad an:")
    return get_browser()

def get_user_data_dir():
    print(f"Meine daten liegen in: {USER_DATA_DIR}")
    user_data_dir = input("Bitte den Pfad zum User Data Ordner angeben:\n")
    user_data_dir = user_data_dir.replace("\\", "/")
    if os.path.exists(user_data_dir):
        return user_data_dir
    else:
        print("Der angegebene Pfad existiert nicht.\nBitte geben Sie den korrekten Pfad an:")
        return get_user_data_dir()


def get_existing_files():
    """Returns a set of already downloaded ZIP filenames."""
    return {f for f in os.listdir(DOWNLOAD_FOLDER) if f.endswith(".zip")}

def get_Website_files():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, executable_path=BROWSER_PATH)
        context = browser.new_context()
        page = context.pages[0] if context.pages else context.new_page()

        print("Navigating to the site...")
        page.goto(BASE_URL, timeout=60000)  # Increase timeout for slow-loading sites
        
        # Wait for user input before continuing
        input("Press Enter after logging in to continue...")

        if page.url != BASE_URL:
            page.goto(BASE_URL, timeout=60000)
        
        print("Extracting download links...")
        links = page.query_selector_all("a.post-attachment-link")  # Adjust selector if needed
        
        zip_links = []
        for link in links:
            href = link.get_attribute("href")
            if href and "file?" in href:
                full_url = urljoin(BASE_URL, href)
                zip_links.append(full_url)
        
        print(f"Found {len(zip_links)} zip files.")
        """
        existing_files = get_existing_files()
        
        for link in zip_links:
            filename = link.split("/")[-1]
            if filename in existing_files:
                print(f"Skipping {filename}, already downloaded.")
                continue
            
            print(f"Downloading {filename}...")
            with page.expect_download() as download_info:
                page.click(f'a[href="{href}"]')  # Click to trigger download
            download = download_info.value
            download_path = os.path.join(DOWNLOAD_FOLDER, filename)
            download.save_as(download_path)
            print(f"Saved {filename} to {download_path}")
        
        print("All missing files downloaded.")"
        """
        browser.close()

# CONFIGURATION
COOKIES_FILE = "cookies.json"  # Store your cookies here
DOWNLOAD_FOLDER = ""
BASE_URL = ""
BROWSER_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe"
USER_DATA_DIR = "C:/Users/YourUsername/AppData/Local/Google/Chrome/User Data"


if __name__ == "__main__":
    DOWNLOAD_FOLDER = get_zip_folder()
    BASE_URL = get_website()
    BROWSER_PATH = get_browser()
    USER_DATA_DIR = get_user_data_dir() # ??? I dont know if this is needed
    
    get_Website_files()
