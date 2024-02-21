import requests
from bs4 import BeautifulSoup

def get_connection(URL):
   print("Establishing connection...")
   try:
      response = requests.get(URL, timeout = 1)
   except requests.exceptions.Timeout:
      raise requests.exceptions.Timeout("Connection failed")
   return response

def get_soup(response):
   soup = BeautifulSoup(response.content, 'html.parser')
   return soup

def get_price(soup):
   try:
      price = soup.find('p', attrs={'class' : 'product-new-price has-deal'}).get_text()
   except AttributeError:
      price = soup.find('p', attrs={'class' : 'product-new-price'}).get_text()
   return price

def find_price(URL):
   return get_price(get_soup(get_connection(URL)))

link_fail = "https://altex.ro/chiuveta-bucatarie-pyramis-altexia-1b1d-70098801-1-cuva-gri/cpd/CVTALTEXI7644CA/"
link = "https://www.emag.ro/set-2-cutie-organizator-medicamente-portabil-amrhaw-plastic-negru-jitoo22740009/pd/DMTPX3YBM/?ref=sponsored_products_p_r_ra_5_2&provider=rec-ads&recid=recads_2_c569e47245778993cb6313c4438115f67244e37ac6628e54061343452949adc0_1708513795&scenario_ID=2&aid=2d330f21-9276-11ee-8d28-0229d980bfff&oid=137169870/"

print(find_price(link))



