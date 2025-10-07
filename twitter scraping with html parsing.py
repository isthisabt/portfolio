import csv
from bs4 import BeautifulSoup

# Define the file paths
html_file_path = r"C:\Users\asadt\OneDrive\Desktop\DRF\Tweets data\(4) kafir - Search _ X (6_8_2024 3_35_58 PM).html"
csv_file_path = r"C:\Users\asadt\OneDrive\Desktop\DRF\Tweets data\kafir.csv"


def extract_username_from_link(link):
    if 'status' in link:
        return link.split('/status')[0].split('/')[-1]
    return 'No username available'


def extract_full_data(html_file_path, csv_file_path):
    # Read the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Prepare the list to store extracted data
    extracted_data = []

    # Find all elements that contain the quoted tweets
    tweet_containers = soup.find_all('article')

    for container in tweet_containers:
        # Extract the link
        link_tag = container.select_one(
            'div > div > div:nth-of-type(2) > div:nth-of-type(2) > div:nth-of-type(1) > div > div:nth-of-type(1) > div > div > div:nth-of-type(2) > div > div:nth-of-type(3) > a')
        if link_tag and 'status' in link_tag['href']:
            link = link_tag['href']
            username = extract_username_from_link(link)
            tweet_text_tag = container.find('div', {'data-testid': 'tweetText'})
            tweet_text = tweet_text_tag.get_text(strip=True) if tweet_text_tag else 'No tweet text available'

            if username != 'No username available':
                extracted_data.append({'Username': username, 'Link': link, 'Tweet Text': tweet_text})

    # Write the extracted data to a CSV file
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Username', 'Link', 'Tweet Text']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in extracted_data:
            writer.writerow(data)

    print(f"Data has been written to {csv_file_path}")


# Call the function
extract_full_data(html_file_path, csv_file_path)

# Display the extracted data
import pandas as pd

df = pd.read_csv(csv_file_path)
df.head()