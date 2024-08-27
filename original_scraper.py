from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import jsonlines
import time

# Set up a rotating User-Agent
ua = UserAgent()

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(f"user-agent={ua.random}")  # Randomize User-Agent

# Initialize the WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Open the target URL
driver.get("https://gian.org/abandoned-us-patents/")

# Allow some time for the JavaScript to load
time.sleep(5)

# Change the number of rows displayed to 100
dropdown = driver.find_element(By.NAME, 'uspto_patents1_length')
dropdown.find_element(By.XPATH, "//option[. = '100']").click()

# Wait for the table to update
time.sleep(5)

# Initialize a JSONL writer
with jsonlines.open('/home/shuvam/statuscode_project/GIAN/abandoned_patents_7.jsonl', mode='w') as writer:
    while True:
        # Extract the page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Find the table by its id
        table = soup.find("table", id="uspto_patents1")
        
        # Loop through each row in the table
        for row in table.find_all("tr")[1:]:  # Skip the header row
            columns = row.find_all("td")
            if len(columns) == 12:  # Ensure that we have 12 columns
                row_data = {
                    "Title": columns[0].get_text(strip=True),
                    "PatentNumber": columns[1].get_text(strip=True),
                    "ApplicationNumber": columns[2].get_text(strip=True),
                    "FilingDate": columns[3].get_text(strip=True),
                    "GrantDate": columns[4].get_text(strip=True),
                    "EntityStatus": columns[5].get_text(strip=True),
                    "ApplicationStatusDate": columns[6].get_text(strip=True),
                    "Id": columns[7].get_text(strip=True),
                    "Type": columns[8].get_text(strip=True),
                    "Abstract": columns[9].get_text(strip=True),
                    "Kind": columns[10].get_text(strip=True),
                    "NumClaims": columns[11].get_text(strip=True)
                }
                # Write each row to the JSONL file immediately
                writer.write(row_data)
        
        # Find and click the 'Next' button using JavaScript
        try:
            next_button = driver.find_element(By.ID, 'uspto_patents1_next')
            
            # Use JavaScript to click the 'Next' button
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(5)  # Adjust this sleep time if needed
            
        except Exception as e:
            print(f"An error occurred: {e}")
            break  # Exit the loop if the 'Next' button cannot be found or clicked

# Close the WebDriver
driver.quit()

print("Data successfully saved to abandoned_patents.jsonl")
