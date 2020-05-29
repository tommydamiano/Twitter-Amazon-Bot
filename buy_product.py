import pymongo
from pymongo import MongoClient
from secrets import cluster
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from time import sleep
import schedule
from secrets import amazon_email, amazon_password

db = cluster['bot']
collection = db['tweet']
collection_items = db['purchased']

# Order tweets by their favorite counts, append purchased items to MongoDB document to ensure item is only purchased once, and call the buy function
def check_tweets():
    data = collection.find().sort('favorites', pymongo.DESCENDING)
    purchased_items = collection_items.find_one()
    for entry in data:
        if str(entry['product_id']) in purchased_items['purchased_items']:
            continue
        else:
            purchased_items['purchased_items'].append(entry['product_id'])
            collection_items.update_one({'identifier': 1}, {'$set': {'purchased_items': purchased_items['purchased_items']}})
            buy(entry['product_id'])
            print(entry['product_id'])
            break

# Use selenium to control browser, login, and buy the product specified by the amazon ID
def buy(amazon_id):
    driver = webdriver.Chrome(executable_path='/Users/thomasdamiano/Driver/chromedriver')
    driver.get("https://www.google.com/")
    search_bar = driver.find_element_by_xpath('//*[@id="tsf"]/div[2]/div[1]/div[1]/div/div[2]/input')
    search_bar.send_keys(amazon_id)
    search_bar.send_keys(Keys.RETURN)
    link = driver.find_element_by_xpath('//*[@id="rso"]/div[1]/div/div[1]/a').click()
    sign_in = driver.find_element_by_xpath('//*[@id="nav-link-accountList"]').click()
    sleep(1)
    email = driver.find_element_by_xpath('//*[@id="ap_email"]')
    email.send_keys(amazon_email)
    email.send_keys(Keys.RETURN)
    sleep(1)
    password = driver.find_element_by_xpath('//*[@id="ap_password"]')
    password.send_keys(amazon_password)
    password.send_keys(Keys.RETURN)
    sleep(1)
    add_to_cart = driver.find_element_by_xpath('//*[@id="add-to-cart-button"]').click()
    sleep(1)
    checkout = driver.find_element_by_xpath('//*[@id="hlb-ptc-btn-native"]').click()
    sleep(1)
    buy = driver.find_element_by_xpath('//*[@id="submitOrderButtonId"]/span/input').click()
    driver.quit() 
    
if __name__ == '__main__':
    # Run the 2 functions every day at 11:59pm
    schedule.every().day.at('23:59').do(check_tweets)
    while 1:
        schedule.run_pending()
        sleep(1)
