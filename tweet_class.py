import re
import requests
import urllib
import pymongo
from pymongo import MongoClient
from bs4 import BeautifulSoup
from secrets import cluster

class Tweet:

    db = cluster['bot']
    collection = db['tweet']

    def __init__(self, **kwargs):
        self.tweet_id = kwargs.get('tweet_id')
        self.username = kwargs.get('username')
        self.content = kwargs.get('content')
        self.favorites = kwargs.get('favorites')
        self.product_url = kwargs.get('product_url', '')
        self.product_id = kwargs.get('product_id', '')
        self.price = kwargs.get('price')

    def check_tweet_content(self, tweet_content):
        url = re.match(r'.*(https://t.co/[^\s]+)\s?', tweet_content)
        if url:
            return url.group(1)

    def get_product_url(self, shorturl):
        r = requests.get(shorturl)
        return r.url

    def get_price(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
        page = requests.get(url, headers= headers)
        soup = BeautifulSoup(page.content, 'html5lib')
        price = soup.find(id= 'priceblock_ourprice').get_text().strip('$')
        return int(price[:-3])

    def insert(self, tweet):
        self.collection.insert_one(tweet)
    
    def update(self, tweet_id, favorites):
        self.collection.update_one({'tweet_id': tweet_id}, {'$set': {'favorites': favorites}})
    
    def fetch(self, tweet_id):
        return self.collection.find_one({'tweet_id': tweet_id})
