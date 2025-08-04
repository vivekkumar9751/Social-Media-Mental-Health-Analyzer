
import tweepy
import pandas as pd
import praw
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('vader_lexicon')

# Twitter API credentials (replace with your own)
bearer_token = "YOUR_BEARER_TOKEN"

# Reddit API credentials (replace with your own)
reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="YOUR_USER_AGENT",
)

def get_twitter_data():
    client = tweepy.Client(bearer_token)
    query = "depression OR anxiety OR burnout -is:retweet"
    tweets = []
    for tweet in tweepy.Paginator(client.search_recent_tweets, query=query, tweet_fields=["created_at", "text", "author_id"], max_results=100).flatten(limit=1000):
        tweets.append([tweet.created_at, tweet.text, tweet.author_id, "Twitter"])
    return pd.DataFrame(tweets, columns=["date", "content", "username", "source"])

def get_reddit_data():
    subreddits = ["depression", "anxiety", "mentalhealth"]
    posts = []
    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        for post in subreddit.hot(limit=100):
            posts.append([pd.to_datetime(post.created_utc, unit='s'), post.title + " " + post.selftext, post.author, "Reddit"])
    return pd.DataFrame(posts, columns=["date", "content", "username", "source"])

if __name__ == "__main__":
    import os

    # Create data directory if it doesn't exist
    output_dir = "../Data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Collecting Twitter data...")
    twitter_df = get_twitter_data()
    print("Collecting Reddit data...")
    reddit_df = get_reddit_data()
    
    df = pd.concat([twitter_df, reddit_df], ignore_index=True)
    output_path = os.path.join(output_dir, "social_media_data.csv")
    df.to_csv(output_path, index=False)
    
    print(f"Data saved to {output_path}")
    print(df.head())
