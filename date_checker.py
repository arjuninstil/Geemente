from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from bs4 import BeautifulSoup 
import time 
import requests 
import urllib.parse 
import datetime
import os

# Safely get environment variables
TOEKN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--remote-debugging-port=9222")

# Use the system chromium-browser
driver = webdriver.Chrome(options=chrome_options)


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
driver = webdriver.Chrome()

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

    # Look for all buttons with class 'list-group-item-action' and not disabled
    available_dates = soup.find_all('button', class_='list-group-item-action')

    alert_no_dates = soup.find_all('div', class_='alert-warning')

    print("alert_no_dates: ", alert_no_dates)


    print(available_dates)
    
    if len(alert_no_dates) == 0:
        print("No available dates alert found.")
        message_first_part="No available dates alert found."
    else:
        message_first_part= "Found something."


    if len(available_dates) == 0:
        # Initialize a list to collect all available dates
        date_info_list = []

        for date_button in available_dates:
            if date_button.get('disabled') is None:
                location = date_button.find('h3').text.strip()
                date_time = date_button.find('p').text.strip()
                # Add each location and date/time to the list
                date_info_list.append(f"{location}: {date_time}")

        # Combine all date information into a single string with line breaks
        date_info = "\n".join(date_info_list)

        # Create the final message
        message = f"{message_first_part}\nAvailable at:\n{date_info}\nMessage Sent at: {current_time}"
        print(message)

        # Send the message via Telegram
        send_telegram_message(message)
    else:
        print("No alert - No available dates found.")

        # Create the message indicating no available dates
        message = f"{message_first_part}\nNo available dates found.\nMessage Sent at: {current_time}"
        #send_telegram_message(message) # Comment this out if you dont want to get messages when there is no dates

finally:
    driver.quit()
