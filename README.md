# Watcher

Watcher is a versatile and user-friendly script designed to enhance your online shopping experience. With Watcher, you can effortlessly manage a personalized watchlist of products from your favorite ecommerce website. The script provides a set of interactive commands that allow you to add, remove, list, and retrieve prices of products directly from the watchlist database.

## Key Features

- **Interactive Management:** Easily add, remove, and list products in your watchlist using intuitive commands, providing a seamless user experience.

- **Real-time Price Updates:** Watcher periodically compares the prices of products stored in your database with the current prices on the ecommerce website. This ensures that you stay informed about any changes, whether it be a price drop or an increase. 

- **Detailed Logging:** The script logs all price comparisons, providing you with a comprehensive history of price changes. This logging feature enables you to track the evolution of prices over time and make informed decisions.

## Limitations and Ongoing Development

- **Single Ecommerce Site Support:** At the moment, Watcher is designed to work with one ecommerce site, [eMAG](https://www.emag.ro/) .

- **Feature 2 (Still in Development):** The feature mentioned in Key Features as "Real-time Price Updates" is currently under development.

## Commands

- `add`: Add a new product to your watchlist.
- `list`: Display the current products in your watchlist.
- `check`: Retrieve the current price of a specific product from the watchlist.
- `remove`: Remove a product from your watchlist.

## Example Interactive Usages

```terminal
python3 -u "watcher_interact.py"

Please select the action you would like to perform [list/check/add/remove]:

>add
Please provide the URL of the product you would like to add to the watchlist:  [Enter URL]
Product added to watchlist!

> list
All products currently watched:
ID = 1 => Product A
ID = 2 => Product B

> check
Please provide the ID of the product you would like to check: [Enter ID]
Current price is: $X.XX

> remove
Please provide the ID of the product you would like to remove from the watchlist: [Enter ID]
Are you sure you want to remove: [Product] from the watchlist? [y/n]: [Enter y/n]
Product removed from watchlist!

```
