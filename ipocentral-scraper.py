import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

# Load IPO data from CSV
input_csv = "past_ipo_data.csv"  # CSV with IPO names and listing dates
output_csv = "ipocentral_articles.csv"

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

# Function to scrape IPO Central for each IPO
def scrape_ipocentral(ipo_name, ipo_date):
    search_url = f"https://ipocentral.in/?s={ipo_name.replace(' ', '+')}"
    driver.get(search_url)
    time.sleep(5)  # Allow JavaScript to load

    soup = BeautifulSoup(driver.page_source, "html.parser")
    articles = soup.find_all("h3", class_="entry-title")  # Adjust if needed

    results = []

    for article in articles:
        try:
            link_elem = article.find("a")  
            link = link_elem["href"] if link_elem else None
            title = link_elem.text.strip() if link_elem else "Unknown Title"

            # Skip if no link found
            if not link:
                continue

            # Open article page
            driver.get(link)
            time.sleep(3)
            article_soup = BeautifulSoup(driver.page_source, "html.parser")

            # Extract article content
            paragraphs = article_soup.find_all("p")
            article_body = " ".join([p.text.strip() for p in paragraphs])

            # Extract author (if available)
            author_elem = article_soup.find("span", class_="author vcard")
            author = author_elem.text.strip() if author_elem else "Unknown"

            # Extract date and convert format
            date_elem = article_soup.find("time", class_="entry-date published")
            if date_elem:
                article_date = datetime.strptime(date_elem.text.strip(), "%B %d, %Y")  # Example: "February 15, 2025"
            else:
                continue  # Skip articles with no date

            # Skip if article date is after the IPO listing date
            if article_date >= ipo_date:
                continue  

            # Store extracted data
            results.append([ipo_name,link, title, author, article_body, article_date.strftime("%Y-%m-%d")])

        except Exception as e:
            print(f"Error processing article for {ipo_name}: {e}")

    return results

# Scrape data for each IPO
scraped_data = []
for ipo in ipo_data:
    print(f"Scraping articles for: {ipo['Name']}")
    scraped_data.extend(scrape_ipocentral(ipo["Name"], ipo["Listing Date"]))

# Save results to CSV
output_df = pd.DataFrame(scraped_data, columns=["IPO Name","Link", "Title", "Author", "Article Body", "Publication Date"])
output_df.to_csv(output_csv, index=False)

# Close Selenium driver
driver.quit()
print(f"Scraping completed! Data saved to {output_csv}")
