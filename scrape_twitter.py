import tweepy
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve API keys from .env
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

# Authenticate with Twitter API
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

# Download NLTK VADER lexicon
nltk.download("vader_lexicon")
sia = SentimentIntensityAnalyzer()

# Load IPO names from CSV
ipo_df = pd.read_csv("past_ipo_data.csv")
ipo_names = ipo_df["Name"].tolist()

# Create a directory for scraped tweets
os.makedirs("tweets", exist_ok=True)

# Function to scrape tweets using Twitter API
def scrape_and_analyze(ipo):
    print(f"Scraping tweets for IPO: {ipo}...")
    
    query = f'"{ipo} IPO" -filter:retweets lang:en'  # Search query
    tweets = []

    try:
        # Fetch tweets
        for tweet in tweepy.Cursor(api.search_tweets, q=query, tweet_mode="extended").items(100):
            tweets.append(tweet.full_text)

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

    except Exception as e:
        print(f"Error scraping {ipo}: {e}")
        return None

# Scrape sentiment for each IPO and store results
sentiment_results = []
for ipo in ipo_names:
    sentiment_score = scrape_and_analyze(ipo)
    sentiment_results.append(sentiment_score if sentiment_score is not None else 0)

# Add sentiment scores to the original dataframe
ipo_df["Average Sentiment"] = sentiment_results

# Save sentiment results
ipo_df.to_csv("ipo_sentiment_results.csv", index=False)
print("Sentiment analysis complete! Results saved to ipo_sentiment_results.csv.")
