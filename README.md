# Zip Scraper
This script is a Python scraper I wrote to download all the zip files within a Patreon collection I subscribed to.
(I was too lazy to manually download 500+ files.)

### ⚠️ Attention!
This script does not work if you are using a Google account to log in, as Google blocks browsers opened by Selenium.
I suspect that Apple and Facebook logins will also not work.

---

## Installation
1. Clone this repository.
2. Install the required dependencies from `requirements.txt`.

---

## Usage
When running this script for the first time, it will ask for:
- The folder where the collection should be downloaded.
- The URL of the desired Patreon collection.
- The URL of the login page (e.g., `https://www.patreon.com/login`).

If you choose to, you can input your login credentials, which will be saved in a `.env` file.
(I plan to add password hashing in the future.)

Once login credentials are provided, the script will log in, retrieve all the zip file download links, and start downloading them automatically.

---

## License
This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.