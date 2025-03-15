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

"""ChatGPT Code"""
def load_cookies(context):
    """Loads cookies into the browser session."""
    try:
        with open(COOKIES_FILE, "r") as f:
            cookies = eval(f.read())  # Load cookies
            context.add_cookies(cookies)
    except FileNotFoundError:
        print("No cookies file found. Please log in manually first and export cookies.")

def get_existing_files():
    """Returns a set of already downloaded ZIP filenames."""
    return {f for f in os.listdir(DOWNLOAD_FOLDER) if f.endswith(".zip")}

def scrape_and_download():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Change to True if you don't need to see the browser
        context = browser.new_context()
        load_cookies(context)
        page = context.new_page()
        
        print("Navigating to the site...")
        page.goto(BASE_URL, timeout=60000)  # Increase timeout for slow-loading sites
        time.sleep(5)  # Give extra time for JS to load content
        
        print("Extracting download links...")
        links = page.query_selector_all("a.post-attachment-link")  # Adjust selector if needed
        
        zip_links = []
        for link in links:
            href = link.get_attribute("href")
            if href and "file?" in href:
                full_url = urljoin(BASE_URL, href)
                zip_links.append(full_url)
        
        print(f"Found {len(zip_links)} zip files.")
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
        
        print("All missing files downloaded.")
        browser.close()

# CONFIGURATION
#COOKIES_FILE = "cookies.json"  # Store your cookies here

if __name__ == "__main__":
    zip_folder = get_zip_folder()
    websiteUrl = get_website()
    #zip_folder = "C:/Users/jan-e/Downloads/Map Collection"
    #scrape_and_download()
