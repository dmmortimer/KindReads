# KindReads
KindReads scripts

## Setup in Shopify Admin

Settings > Apps and Sales Channels > Develop Apps > Enable Custom App Development

Create an App > Kind Reads Book Inventory

Configuration > Admin API integration

Admin API access scopes read_products, read_orders

API Credentials > Admin API access token (deliberately not committed to GitHub)

## Scripts overview
getproducts.py
- downloads all products into a combined products.json file called products-all.json

validatetags.py
- has functions to validate tags for consistency, and to derive expected Room 149 shelf from tags
- if called as a standalone program, reads products-all.json and outputs a csv of books with tag errors

listproducts.py
- reads products-all.json and outputs products-in-stock.csv with tags and expected shelf for each book

getorders.py
- fetches all orders then fetches each line item and outputs a csv of books in orders, with tags
- expensive to do all orders, use carefully
