import requests
from bs4 import BeautifulSoup
import webbrowser
import time
from price_parser import Price
import mysql.connector
import configparser

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

#Compares the last recorded price and the current price and returns the change if any 
def compare_price(old_price,current_price):
   if old_price == current_price:
      return "No changes"
   else:
      return "The price changed from " + old_price + " to " + current_price
   
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
      "INSERT INTO test (id, Name, URL, Price) "
      "VALUES (NULL, %s, %s, %s)"
   )
   data = (get_product_title(url), url, current_price(url))
   cursor.execute(command,data)
   conn.commit()

#Fetch the price of a product from the database
def fetch_product_price(id, cursor):
   command = (
      "SELECT Price FROM test WHERE test.id = %s"
   )
   data = (id,)
   #Handle a wrong ID
   try:
      cursor.execute(command,data)
      price = cursor.fetchone()[0]
      return price
   except TypeError:
      return None

#Delete a product from the database
def delete_product_watch(url, conn, cursor):
   command = (
      "DELETE FROM test WHERE test.URL = %s"
   )
   data = (url,)
   cursor.execute(command,data)
   conn.commit()

#Print a list of all products currently in the database with their ID
def list_all_products(cursor):
   command = (
      "SELECT id, Name FROM test"
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
      link = input("Please provide the URL of the product you would like to remove from the watchlist: ")
      delete_product_watch(link, conn, cursor)
      print("Product removed from watchlist")
   else:
      print("No option with this name!")
   
   if input("Would you like to perform another action? [y/n]: ") == "y":
      interact_with_db()

   if conn.is_connected() == True:
      conn.close()

#Hard coded test links
link_fail = "https://altex.ro/chiuveta-bucatarie-pyramis-altexia-1b1d-70098801-1-cuva-gri/cpd/CVTALTEXI7644CA/"
link3 = "https://www.emag.ro/set-2-cutie-organizator-medicamente-portabil-amrhaw-plastic-negru-jitoo22740009/pd/DMTPX3YBM/?ref=sponsored_products_p_r_ra_5_2&provider=rec-ads&recid=recads_2_c569e47245778993cb6313c4438115f67244e37ac6628e54061343452949adc0_1708513795&scenario_ID=2&aid=2d330f21-9276-11ee-8d28-0229d980bfff&oid=137169870/"
link2 = "https://www.emag.ro/set-12-martisoare-bratari-nevermore-fluture-colorate-lungime-reglabila-rosu-n1006/pd/DK9X0KYBM/"

interact_with_db()
