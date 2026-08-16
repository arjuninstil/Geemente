from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import re
import time
import requests
import urllib.parse
import datetime

# Safely get environment variables
TOKEN = "8968926811:AAEduM3RXFH8DjFFE7QfFBVlOO5srge8_zE"#os.getenv("TOKEN")
CHAT_ID = "8818555435"#os.getenv("CHAT_ID")

print(TOKEN, CHAT_ID)


def is_real_appointment(date_time_text):
    """Return True only for actual bookable slots, not waitlist placeholders."""
    text = date_time_text.lower().strip()
    if not text:
        return False
    if "wachtrij" in text:
        return False
    # Real slots contain a date or time (e.g. "20 januari 2025" or "10:00")
    return bool(re.search(r"\d", text))


def collect_available_dates(soup):
    date_buttons = soup.find_all("button", class_="list-group-item-action")
    available_dates = []

    for date_button in date_buttons:
        if date_button.get("disabled") is not None:
            continue
        location_el = date_button.find("h3")
        date_time_el = date_button.find("p")
        if not location_el or not date_time_el:
            continue

        location = location_el.get_text(strip=True)
        date_time = date_time_el.get_text(strip=True)
        if is_real_appointment(date_time):
            available_dates.append(f"{location}: {date_time}")

    return available_dates


def create_driver():
    options = Options()
    if os.getenv("GITHUB_ACTIONS") == "true" or os.getenv("CI"):
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

# Function to send a Telegram message
def send_telegram_message(message):
    bot_token = TOKEN  # Replace with your bot token
    chat_ids = [CHAT_ID] #, add more than one if you want to]
    


    # Properly encode the message text to be URL-safe
    encoded_message = urllib.parse.quote(message)
    for chat_id in chat_ids:
            send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={encoded_message}'
            
            # Send message to each chat ID
            response = requests.get(send_text)

            if response.status_code == 200:
                print(f"Telegram message sent successfully to chat ID: {chat_id}!")
            else:
                print(f"Failed to send message to chat ID: {chat_id}. Status code: {response.status_code}, response: {response.text}")


# Selenium 4+ auto-downloads the matching ChromeDriver for your installed Chrome
driver = create_driver()

# Open the local HTML file or directly access the URL if it's online
driver.get("https://concern.ir.rotterdam.nl/afspraak/maken/product/indienen-naturalisatieverzoek") 


try:
    # Get the current date and time
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    time.sleep(2) 
    # Wait for the "Verder" button to be clickable and click it
    verder_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "verder"))
    )
    verder_button.click()

    # Wait for the page to load and the dates to appear (adjust timeout as needed)
    time.sleep(2)  # or use WebDriverWait to wait for specific elements to appear

    # Parse the updated HTML content with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    available_dates = collect_available_dates(soup)
    print("available_dates:", available_dates)

    if available_dates:
        date_info = "\n".join(available_dates)
        message = f"Dates available!\nAvailable at:\n{date_info}\nMessage sent at: {current_time}"
        print(message)
        send_telegram_message(message)
    else:
        print("No available dates found. No message sent.")
        message = f"Dates available!\nAvailable at:\nNone\nMessage sent at: {current_time}"
        send_telegram_message(message)

finally:
    driver.quit()
