from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Set up WebDriver (make sure you have ChromeDriver installed)
driver = webdriver.Chrome()

# Open Twitter
driver.get("https://twitter.com/login")
time.sleep(3)

# Enter username
username = driver.find_element(By.NAME, "session[username_or_email]")
username.send_keys("your_username")
time.sleep(1)

# Enter password
password = driver.find_element(By.NAME, "session[password]")
password.send_keys("your_password")
password.send_keys(Keys.RETURN)
time.sleep(5)

# Search for IPO-related tweets
search_box = driver.find_element(By.XPATH, '//input[@aria-label="Search query"]')
search_box.send_keys("Hexaware IPO")
search_box.send_keys(Keys.RETURN)
time.sleep(5)

# Get tweets
tweets = driver.find_elements(By.XPATH, '//div[@data-testid="tweetText"]')
for tweet in tweets:
    print(tweet.text)

# Close browser
driver.quit()
