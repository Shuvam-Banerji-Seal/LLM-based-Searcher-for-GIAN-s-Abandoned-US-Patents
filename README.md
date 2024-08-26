

# LLM-based-Searcher-for-GIAN's Abandoned US Patents

This repository contains the first part of the **LLM-based-Searcher-for-GIAN's Abandoned US Patents** project. The goal of this project is to create a better and more efficient searching application for the GIAN abandoned US patents database.

## Data Extractor

The data extractor script automates the process of extracting data from GIAN's abandoned US patents webpage, which contains over 10 lakh rows. The extracted data is stored in JSON Lines format (`.jsonl`), allowing for easy line-by-line processing in the next stages of the project.

### Features

- **Automated Web Scraping**: Uses Selenium to navigate the website and handle dynamic JavaScript content.
- **Data Storage**: Extracted patent data is stored in a `.jsonl` file, with each patent record written as a single JSON object.
- **Rotating User-Agent**: To avoid detection, the script uses `fake_useragent` to rotate user agents.
- **Headless Mode**: The browser operates in headless mode, running without a graphical interface to increase speed and efficiency.
- **Error Handling**: The script captures any errors encountered during the extraction process, such as issues with page navigation.

### Prerequisites

Before running the script, ensure you have the following installed:

- Python 3.x
- Selenium
- BeautifulSoup (`bs4`)
- Chrome WebDriver
- `jsonlines`
- `fake_useragent`

You can install the necessary packages using pip:

```bash
pip install selenium beautifulsoup4 jsonlines fake-useragent
```

### Usage

1. **Set Up ChromeDriver**: Download and install the Chrome WebDriver compatible with your Chrome browser version. Ensure that the WebDriver is accessible via your system's PATH.

2. **Run the Script**: After setting up the environment, run the script to start extracting the patent data. The script will navigate to the [GIAN abandoned US patents page](https://gian.org/abandoned-us-patents/), set the view to 100 rows per page, and begin scraping data.

```bash
python data_extractor.py
```

3. **Output**: The extracted data will be saved to a `.jsonl` file located in the specified directory (e.g., `abandoned_patents_7.jsonl`).

### Example Data

Each row of the output JSONL file will contain fields like:

```json
{
  "Title": "Sample Patent Title",
  "PatentNumber": "1234567",
  "ApplicationNumber": "0987654",
  "FilingDate": "2021-01-01",
  "GrantDate": "2021-12-31",
  "EntityStatus": "Active",
  "ApplicationStatusDate": "2021-12-31",
  "Id": "1",
  "Type": "Utility",
  "Abstract": "A sample abstract of the patent...",
  "Kind": "A1",
  "NumClaims": "10"
}
```

### Error Handling

The script includes error handling mechanisms to stop the extraction process gracefully if issues occur, such as the inability to locate the 'Next' button.

### Roadmap

- **Phase 1**: Data extraction and storage (current phase).
- **Phase 2**: Building the LLM-based search engine using the extracted data.

### Contributing

Feel free to open an issue or submit a pull request if you want to contribute to the project. Contributions are always welcome!

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.



