import requests
from bs4 import BeautifulSoup
import webbrowser
import time
from price_parser import Price
import mysql.connector
import configparser
import logging

#Connects to the URL and returns the HTTPS response
def get_connection(url):
   #Tries to get a response and raises and error in case of a timeout
   try:
      response = requests.get(url, timeout = 1)
   except requests.exceptions.Timeout:
      raise requests.exceptions.Timeout("Connection timed out!")
   
   #Reauthenticate user if too many requests are made
   if response.status_code == 511:
      webbrowser.open(url)
      print("Please validate your connection!")
      time.sleep(5)
      #Restart the function in case of a 511 response
      get_connection(url)

   return response

#Parse the received HTML response and return soup object
def get_soup(response):
   soup = BeautifulSoup(response.content, 'html.parser')
   return soup

#Retrive the price from the soup
def get_price(soup):
   try:
      price = soup.find('p', attrs={'class' : 'product-new-price has-deal'}).get_text()
   except AttributeError:
      price = soup.find('p', attrs={'class' : 'product-new-price'}).get_text()

   return price.lower()

#Returns the current price of the product
def current_price(url):
   return parse_price(get_price(get_soup(get_connection(url))))
   
#Get the string price and make it float
def parse_price(str_price):
   price = Price.fromstring(str_price)
   return price.amount_float

#Returns the title of the products based on the URL
def get_product_title(url):
   soup = get_soup(get_connection(url))
   return soup.title.text

#Connect to the database and initialize the cursor
def connect_to_db():
   config = configparser.ConfigParser()
   config.read("db_config.ini")

   conn = mysql.connector.connect(
      host = config.get('Database','host'),
      user = config.get('Database','user'),
      password = config.get('Database','password'),
      database = config.get('Database','database')
   )
   cursor = conn.cursor()
   return conn,cursor

#Add a product to the database
def add_product_watch(url, conn, cursor):
   command = (
      "INSERT INTO watcher (id, Name, URL, Price) "
      "VALUES (NULL, %s, %s, %s)"
   )
   title = get_product_title(url)
   data = (title, url, current_price(url))
   cursor.execute(command,data)
   conn.commit()
   log_event('add', title)

#Fetch the price of a product from the database
def fetch_product_price(id, cursor):
   command = (
      "SELECT Price FROM watcher WHERE watcher.id = %s"
   )
   data = (id,)
   #Handle a wrong ID
   try:
      cursor.execute(command,data)
      price = cursor.fetchone()[0]
      return price
   except TypeError:
      return None
   
#Fetch the name of a product from the database
def fetch_product_name(id, cursor):
   command = (
      "SELECT Name FROM watcher WHERE watcher.id = %s"
   )
   data = (id,)
   #Handle a wrong ID
   try:
      cursor.execute(command,data)
      name = cursor.fetchone()[0]
      return name
   except TypeError:
      return None

#Delete a product from the database
def delete_product_watch(id, conn, cursor):
   command = (
      "DELETE FROM watcher WHERE watcher.id = %s"
   )
   title = fetch_product_name(id, cursor)
   data = (id,)
   cursor.execute(command,data)
   conn.commit()
   log_event('delete', title)

#Print a list of all products currently in the database with their ID
def list_all_products(cursor):
   command = (
      "SELECT id, Name FROM watcher"
   )
   cursor.execute(command)
   id_names = cursor.fetchall()
   for id_name in id_names:
      print("ID = " + str(id_name[0]),"=> " + str(id_name[1]))


#All the available interaction options with the database
def interact_with_db():
   conn, cursor = connect_to_db()

   mode = input("Please select the action you would like to perform [list/check/add/remove]: ")

   if mode == "list":
      print("All products currently watched:")
      list_all_products(cursor)

   elif mode == "add":
      link = input("Please provide the URL of the product you would like to add to the watchlist: ")
      add_product_watch(link,conn,cursor)
      print("Product added to watchlist")

   elif mode == "check":
      id = input("Please provide the ID of the product you would like to check: ")
      price = fetch_product_price(id,cursor)
      if price != None:
         print("Current price is: "+ str(price))
      else:
         print("No product with the given ID!")

   elif mode == "remove":
      id = input("Please provide the ID of the product you would like to remove from the watchlist: ")
      prod_name = fetch_product_name(id,cursor)
      if prod_name != None:
         if input("Are you sure you want to remove: " + str(prod_name) + " from the watchlist? [y/n]: ") == "y":
            delete_product_watch(id, conn, cursor)
            print("Product removed from watchlist")
         else:
            print("Operation aborted!")
      else:
         print("No product with the given ID!")

   else:
      print("No option with this name!")
   
   if input("Would you like to perform another action? [y/n]: ") == "y":
      interact_with_db()

   if conn.is_connected() == True:
      conn.close()

#Log events like adding, deleting and checking products from the watchlist
def log_event(type,arg):
   
   ADD = 27
   DELETE = 26
   CHECK = 25
   logging.addLevelName(ADD, 'ADD')
   logging.addLevelName(DELETE, 'DELETE')
   logging.addLevelName(CHECK, 'CHECK')

   FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
   logging.basicConfig(filename = "watcher.log", level = logging.INFO, format= FORMAT)

   if type == 'add':
      logging.log(ADD, "Product (" + arg + ") has been added to the watchlist")
   elif type == 'delete':
      logging.log(DELETE, "Product (" + arg + ") has been removed from the watchlist")
   elif type == 'check':
      logging.log(CHECK, arg)

#Runs auto checks for price changes every n hours
def auto_check(conn,cursor):
   command = (
      "SELECT URL, Price, Name FROM watcher"
   )
   cursor.execute(command)
   urls_prices_names = cursor.fetchall()
   for url_price_name in urls_prices_names:
      price_now = current_price(url_price_name[0])
      price_change = compare_price(url_price_name[1], price_now, url_price_name[2])
      if price_change == 'change':
         command = (
            "UPDATE watcher SET Price = %s WHERE Name = %s" 
         )
         data = (price_now,url_price_name[2])
         cursor.execute(command,data)
         conn.commit()

#Compares the last recorded price and the current price and returns the change if any 
def compare_price(old_price,current_price,product_name):
   if old_price == current_price:
      log_event('check', product_name + " - price hasn't changed!")
   elif old_price < current_price:
      price_change = current_price - old_price
      log_event('check', product_name + " - price incresed by " + str(price_change))
      return 'change'
   elif old_price > current_price:
      price_change = old_price - current_price
      log_event('check', product_name + " - price decresed by " + str(price_change))
      return 'change'