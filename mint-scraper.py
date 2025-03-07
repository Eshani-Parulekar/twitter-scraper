import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

# Load IPO data from CSV
input_csv = "past_ipo_data.csv"  # CSV with IPO names and listing dates
output_csv = "mint_articles.csv"

df = pd.read_csv(input_csv)  

# Convert listing date to datetime format
df["Listing Date"] = pd.to_datetime(df["Listing Date"], format="%d-%b-%y")  # Example: 21-Feb-25 → 2025-02-21
ipo_data = df[["Name", "Listing Date"]].to_dict(orient="records")

# Set up Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Function to scrape The Mint website for each IPO
def scrape_mint(ipo_name, ipo_date):
    search_url = f"https://www.livemint.com/Search/Link/Keyword/{ipo_name.replace(' ', '%20')}"
    driver.get(search_url)
    time.sleep(5)  # Allow JavaScript to load

    soup = BeautifulSoup(driver.page_source, "html.parser")
    articles = soup.find_all("div", class_="headlineSec")  # Adjust class name based on actual structure

    results = []

    for article in articles:
        try:
            title_elem = article.find("h2", class_="headline")  # Article title
            link = title_elem.find("a")["href"] if title_elem else None
            date_elem = article.find("span", class_="date")  # Publication date
            author_elem = article.find("span", class_="author")  # Author name
            
            if link and date_elem:
                article_url = f"https://www.livemint.com{link}"
                article_date = datetime.strptime(date_elem.text.strip(), "%d %b %Y")  # Example: "21 Feb 2025"

                # Skip if article date is after the IPO listing date
                if article_date >= ipo_date:
                    continue  

                # Open article page
                driver.get(article_url)
                time.sleep(3)
                article_soup = BeautifulSoup(driver.page_source, "html.parser")

                # Extract article content
                paragraphs = article_soup.find_all("p")
                article_body = " ".join([p.text.strip() for p in paragraphs])

                # Store extracted data
                results.append([ipo_name, link, author_elem.text.strip() if author_elem else "Unknown", article_body, article_date.strftime("%Y-%m-%d")])

        except Exception as e:
            print(f"Error processing article for {ipo_name}: {e}")

    return results

# Scrape data for each IPO
scraped_data = []
for ipo in ipo_data:
    print(f"Scraping articles for: {ipo['Name']}")
    scraped_data.extend(scrape_mint(ipo["Name"], ipo["Listing Date"]))

# Save results to CSV
output_df = pd.DataFrame(scraped_data, columns=["IPO Name", "Link", "Author", "Article Body", "Publication Date"])
output_df.to_csv(output_csv, index=False)

# Close Selenium driver
driver.quit()
print(f"Scraping completed! Data saved to {output_csv}")
