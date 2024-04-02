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
- by default, downloads all active products
- if products.txt is present, downloads products by ISBN listed one per line in products.txt
- outputs a file called products-all.json for use with validatetags or listproducts or getlibdiscard

getlibdiscard.py
- reads products-all.json and fetches library_discard metafield for each product
- expensive, takes over 15 minutes to run, only use if library_discard value is needed in a report
- writes updated products-all.json for use with listproducts

validatetags.py
- has functions to validate tags for consistency, and to derive expected Room 149 shelf from tags
- if called as a standalone program, reads products-all.json and outputs a csv of books with tag errors

listproducts.py
- reads products-all.json and outputs products-in-stock.csv with tags and expected shelf for each book

getorders.py
- fetches all orders then fetches each line item and outputs a csv of books in orders, with tags
- expensive to do all orders, use carefully

fopla_csv_generator.rb
 - Ruby script that reads ISBNs from file scans.csv, pulls book information via API and outputs a CSV for uploading to Shopify
 - Outputs up to three CSVs:
   - Completed book profiles (meaning all of the attributes have a value)
   - Incomplete (meaning the book was found in the db, but not all attributes were retrievable)
   - Not found (ISBNs weren't in the db)
 - Requires API token obtained separately
 - API documentation here: https://isbndb.com/apidocs/v2

 ## CSV validation web app
 A simple web app is deployed at https://dmortimer.pythonanywhere.com so volunteers working on scan uploads
 can validate the product CSV file including book cover images before it is imported into Shopify.

 flask_app.py - web app using Flask framework
 
 validatecsv.py - processing code for the web app, calling functions from validatetags.py to do the real work
 
 static/images folder - images for the web app
 
 templates folder - html pages for the web app
