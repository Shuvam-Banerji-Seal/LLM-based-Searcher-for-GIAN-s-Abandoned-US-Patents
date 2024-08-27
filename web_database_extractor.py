import os
import time
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from ttkthemes import ThemedTk
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import jsonlines
import json
from fake_useragent import UserAgent

class PatentScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Patent Scraper")

        # Enable window resizing
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Create a frame to contain all elements
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(sticky=tk.NSEW)

        # Directory selection
        self.dir_label = ttk.Label(main_frame, text="Select Output Directory:")
        self.dir_label.grid(row=0, column=0, sticky=tk.W)

        self.dir_button = ttk.Button(main_frame, text="Browse", command=self.select_directory)
        self.dir_button.grid(row=0, column=1, sticky=tk.E)

        self.selected_dir = tk.StringVar()
        self.selected_dir_label = ttk.Label(main_frame, textvariable=self.selected_dir, relief=tk.SUNKEN)
        self.selected_dir_label.grid(row=1, column=0, columnspan=2, sticky=tk.EW)

        # File name entry
        self.file_label = ttk.Label(main_frame, text="Enter Output File Name:")
        self.file_label.grid(row=2, column=0, sticky=tk.W)

        self.file_entry = ttk.Entry(main_frame)
        self.file_entry.insert(0, "abandoned_patents.jsonl")
        self.file_entry.grid(row=2, column=1, sticky=tk.EW)

        # Start and Stop buttons
        self.start_button = ttk.Button(main_frame, text="Start Scraping", command=self.start_scraping)
        self.start_button.grid(row=3, column=0, pady=10, sticky=tk.EW)
        
        self.stop_button = ttk.Button(main_frame, text="Stop Scraping", command=self.stop_scraping, state=tk.DISABLED)
        self.stop_button.grid(row=3, column=1, pady=10, sticky=tk.EW)

        # Status label
        self.status_label = ttk.Label(main_frame, text="Status: Idle", foreground="green")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=10)

        # Progress text box
        self.progress_text = tk.Text(main_frame, height=10, width=60, wrap=tk.WORD)
        self.progress_text.grid(row=5, column=0, columnspan=2, sticky=tk.NSEW)

        # Scraped data text box
        self.data_text = tk.Text(main_frame, height=10, width=60, wrap=tk.WORD, bg="#f0f0f0")
        self.data_text.grid(row=6, column=0, columnspan=2, sticky=tk.NSEW)

        # Configure grid layout for scaling
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Control variables
        self.scraping_active = False

    def select_directory(self):
        """Open a dialog to select the output directory."""
        directory = filedialog.askdirectory()
        if directory:
            self.selected_dir.set(directory)

    def log_progress(self, message):
        """Log progress to the GUI and the console."""
        self.progress_text.insert(tk.END, message + '\n')
        self.progress_text.see(tk.END)
        print(message)  # Print to console for real-time tracking

    def display_data(self, data):
        """Display scraped data in the data text box."""
        self.data_text.insert(tk.END, data + '\n')
        self.data_text.see(tk.END)

    def setup_driver(self):
        """Set up the Chrome WebDriver with necessary options."""
        ua = UserAgent()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={ua.random}")
        self.log_progress("Chrome WebDriver initialized.")
        return webdriver.Chrome(options=chrome_options)

    def start_scraping(self):
        """Start the scraping process in a separate thread to avoid blocking the GUI."""
        self.status_label.config(text="Status: Running", foreground="blue")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Ensure that a directory and file name have been set
        directory = self.selected_dir.get()
        file_name = self.file_entry.get()

        if not directory or not file_name:
            messagebox.showwarning("Input Error", "Please select a directory and enter a valid file name.")
            self.status_label.config(text="Status: Idle", foreground="green")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            return

        file_path = os.path.join(directory, file_name)

        # Start the scraping thread
        self.scraping_active = True
        threading.Thread(target=self.run_scraper, args=(file_path,)).start()

    def stop_scraping(self):
        """Stop the scraping process."""
        self.scraping_active = False
        self.status_label.config(text="Status: Stopping...", foreground="red")

    def run_scraper(self, file_path):
        """Run the scraping task in the background."""
        driver = self.setup_driver()

        try:
            # Open the target URL
            driver.get("https://gian.org/abandoned-us-patents/")
            self.log_progress("Opened the target URL.")
            time.sleep(5)

            # Change the number of rows displayed to 100
            dropdown = driver.find_element(By.NAME, 'uspto_patents1_length')
            dropdown.find_element(By.XPATH, "//option[. = '100']").click()
            self.log_progress("Set the number of rows displayed to 100.")
            time.sleep(5)

            # Initialize the JSONL writer
            with jsonlines.open(file_path, mode='w') as writer:
                page_count = 0

                while self.scraping_active:
                    page_count += 1
                    self.log_progress(f"Scraping page {page_count}...")

                    # Extract the page source and parse with BeautifulSoup
                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    table = soup.find("table", id="uspto_patents1")

                    # Loop through each row in the table
                    for row in table.find_all("tr")[1:]:
                        columns = row.find_all("td")
                        if len(columns) == 12:
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
                            writer.write(row_data)
                            self.display_data(json.dumps(row_data, indent=4))  # Display formatted data in GUI

                    # Click the 'Next' button if available
                    try:
                        next_button = driver.find_element(By.ID, 'uspto_patents1_next')
                        driver.execute_script("arguments[0].click();", next_button)
                        self.log_progress("Clicked 'Next' button.")
                        time.sleep(5)
                    except Exception as e:
                        self.log_progress(f"Error occurred: {e}")
                        break

        except Exception as e:
            self.log_progress(f"Exception occurred: {e}")
        finally:
            driver.quit()
            self.status_label.config(text="Status: Idle", foreground="green")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.scraping_active = False

if __name__ == "__main__":
    root = ThemedTk(theme="arc")  # Using the modern Arc theme
    scraper_gui = PatentScraperGUI(root)
    root.mainloop()
