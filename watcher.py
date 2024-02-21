import requests
from bs4 import BeautifulSoup
import webbrowser
import time

#Connects to the URL and returns the HTTPS response
def get_connection(url):
   print("Establishing connection...")
   #Tries to get a response and raises and error in case of a timeout
   try:
      response = requests.get(url, timeout = 1)
   except requests.exceptions.Timeout:
      raise requests.exceptions.Timeout("Connection timed out!")
   
   #Reauthenticate user if too many requests are made
   if response.status_code == 511:
      webbrowser.open(url)
      print("Please validate your connection!")
      time.wait(10)

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

   return price

#Combines everything togheter
def find_price(url):
   return get_price(get_soup(get_connection(url)))

#Hard coded test links
link_fail = "https://altex.ro/chiuveta-bucatarie-pyramis-altexia-1b1d-70098801-1-cuva-gri/cpd/CVTALTEXI7644CA/"
link = "https://www.emag.ro/set-2-cutie-organizator-medicamente-portabil-amrhaw-plastic-negru-jitoo22740009/pd/DMTPX3YBM/?ref=sponsored_products_p_r_ra_5_2&provider=rec-ads&recid=recads_2_c569e47245778993cb6313c4438115f67244e37ac6628e54061343452949adc0_1708513795&scenario_ID=2&aid=2d330f21-9276-11ee-8d28-0229d980bfff&oid=137169870/"

print(find_price(link))

