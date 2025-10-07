import requests
import pandas as pd

# Replace 'your_bearer_token' with your actual Bearer Token
BEARER_TOKEN = 'hidden_token'

# Twitter API endpoint for searching tweets
SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"

# The query keyword you're searching for
QUERY = 'kafir'


# Function to create headers for the HTTP request
def create_headers(bearer_token):
    headers = {"Authorization": "Bearer " + bearer_token}
    return headers


# Function to get tweets from the API
def get_tweets(headers, url, query, next_token=None):
    params = {
        'query': query,
        'tweet.fields': 'author_id,created_at,text',
        'max_results': 200  # Adjust max_results as needed, max is 100
    }
    if next_token:
        params['next_token'] = next_token
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception("Request returned an error: {} {}".format(response.status_code, response.text))
    return response.json()


# Main function
def main():
    headers = create_headers(BEARER_TOKEN)
    next_token = None
    all_tweets = []

    while True:
        tweets = get_tweets(headers, SEARCH_URL, QUERY, next_token)
        tweet_data = [{
            'id': tweet['id'],
            'author_id': tweet['author_id'],
            'text': tweet['text'],
            'created_at': tweet['created_at']
        } for tweet in tweets['data']]
        all_tweets.extend(tweet_data)

        # Check if there is a next_token to fetch the next page of results
        if 'meta' in tweets and 'next_token' in tweets['meta']:
            next_token = tweets['meta']['next_token']
        else:
            break

    # Convert to DataFrame and save as CSV
    df = pd.DataFrame(all_tweets)
    df.to_csv('tweets.csv', index=False)
    print(f"Saved {len(all_tweets)} tweets to tweets.csv")


# Run the main function
if __name__ == "__main__":
    main()

