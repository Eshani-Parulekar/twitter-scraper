from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import time
import os

# Download VADER lexicon
nltk.download("vader_lexicon")
sia = SentimentIntensityAnalyzer()

# Load IPO names from CSV
ipo_df = pd.read_csv("past_ipo_data.csv")
ipo_names = ipo_df["Name"].tolist()

# Create a directory for scraped tweets
os.makedirs("tweets", exist_ok=True)

# Set up Selenium Chrome driver
chrome_options = Options()
chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # Manually set path
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Function to scrape tweets using BeautifulSoup
def scrape_and_analyze(ipo):
    print(f"Scraping tweets for IPO: {ipo}...")

    search_url = f"https://twitter.com/search?q={ipo}%20IPO&f=live"
    driver.get(search_url)
    time.sleep(5)  # Let the page load

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Find all tweets
    tweets = []
    for tweet in soup.find_all("div", {"data-testid": "tweetText"}):
        tweets.append(tweet.get_text())

    if not tweets:
        print(f"No tweets found for {ipo}. Skipping...")
        return None

    # Perform sentiment analysis
    sentiments = [sia.polarity_scores(tweet)["compound"] for tweet in tweets]

    # Save tweets
    tweets_df = pd.DataFrame({"tweet": tweets, "sentiment": sentiments})
    tweets_df.to_csv(f"tweets/{ipo}_tweets.csv", index=False)

    # Aggregate sentiment
    avg_sentiment = sum(sentiments) / len(sentiments)
    return avg_sentiment

# Scrape sentiment for each IPO
sentiment_results = []
for ipo in ipo_names:
    sentiment_score = scrape_and_analyze(ipo)
    sentiment_results.append(sentiment_score if sentiment_score is not None else 0)

# Add sentiment scores to the original dataframe
ipo_df["Average Sentiment"] = sentiment_results

# Save sentiment results
ipo_df.to_csv("ipo_sentiment_results.csv", index=False)

# Close Selenium driver
driver.quit()

print("Sentiment analysis complete! Results saved to ipo_sentiment_results.csv.")
