import re
import tweepy
from tweet_class import Tweet
from time import sleep
import schedule
import webbrowser

API_KEY = ''
API_PO = ''
ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''
auth = tweepy.OAuthHandler(API_KEY, API_PO)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
name = 'tommydfor3_'

# Function to search twitter for all replies to the username @tommydfor3_, check if it contains a valid amazon link, and then send tweet to MongoDB datbase
def get_tweets():
    for tweet in tweepy.Cursor(api.search, q= f'to:{name}', result_type= 'recent', timeout= 999999).items(1000):
        new_tweet = Tweet(tweet_id= tweet.id_str, username= tweet.user.screen_name, content= tweet.text, favorites= api.get_status(tweet.id).favorite_count)
        shorturl = new_tweet.check_tweet_content(new_tweet.content)
        if shorturl:
            url = new_tweet.get_product_url(shorturl)
            if 'amazon' in url:
                try:
                    price = new_tweet.get_price(url)
                    if price > 20:
                        continue
                except:
                    continue
                product_id = re.match("http[s]?://www.amazon.(\w+)(.*)/(dp|gp/product)/(?P<asin>\w+).*", url, flags=re.IGNORECASE)
                if product_id:
                    new_tweet.price, new_tweet.product_url, new_tweet.product_id = price, url, product_id.group(4)
                    result = new_tweet.fetch(new_tweet.tweet_id)
                    # If tweet is already in the database, update its favorites count instead of inserting again
                    if result:
                        new_tweet.update(new_tweet.tweet_id, new_tweet.favorites)
                    else:
                        new_tweet.insert(new_tweet.__dict__)

if __name__ == '__main__':
    # Run the get_tweets function every 30 minutes
    schedule.every(30).minutes.do(get_tweets)
    while 1:
        schedule.run_pending()
        sleep(1)
