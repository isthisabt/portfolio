from bs4 import BeautifulSoup
from selenium import webdriver
import time


# Function to add the next cursor and return the updated URL
def add_next_cursor(driver, my_url):
    driver.get(my_url)
    time.sleep(5)

    resp = driver.page_source
    soup = BeautifulSoup(resp, 'html.parser')

    show_more_divs = soup.find_all("div", {"class": "show-more"})
    if len(show_more_divs) >= 2:
        profile_header = show_more_divs[1]
        cursor = profile_header.find('a').get('href')
        return cursor
    else:
        profile_header = soup.find("div", {"class": "show-more"})
        cursor = profile_header.find('a').get('href')
    return cursor


# Function to scrape tweets and save them to a file
def scrape_tweets_and_save(hashtag, num_tweets, output_file, max_urls):
    driver = webdriver.Chrome()
    driver.get("https://nitter.net/search?f=tweets&q=" + hashtag)
    time.sleep(5)

    # Allow time for manual login input
    input("Please manually enter search query. Press Enter to continue...")

    cursor = ""
    urls = []
    url_count = 0

    while True:
        try:
            cursor = add_next_cursor(driver, "https://nitter.net/search?f=tweets&q=" + hashtag + cursor)
            if not cursor:
                break
            urls.append("https://nitter.net/search?f=tweets&q=" + hashtag + cursor)
            url_count += 1
            if url_count >= max_urls:
                break
            print(f"Loading more tweets from {cursor}")
        except:
            print("Reached the end, ending the program…")
            break

    driver.quit()

    with open(output_file, 'w', encoding='utf-8') as file:
        for url in urls:
            driver = webdriver.Chrome()
            driver.get(url)
            time.sleep(5)

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            tweet_divs = soup.find_all('div', class_='tweet-content media-body')

            for i, tweet_div in enumerate(tweet_divs[:num_tweets]):
                tweet_text = tweet_div.get_text(strip=True)
                file.write(f"{i + 1}. {tweet_text}\n")
                file.write('-' * 50 + '\n')

                print(f"{i + 1}. {tweet_text}")
                print('-' * 50)

            driver.quit()


if __name__ == "__main__":
    hashtag_to_scrape = "aurat"
    number_of_tweets = 30
    output_filename = "tweets_output.txt"
    max_urls_to_collect = 10  # Change this to the desired number of URLs depending on time and amount of data

    scrape_tweets_and_save(hashtag_to_scrape, number_of_tweets, output_filename, max_urls_to_collect)
