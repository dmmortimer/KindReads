import json
import requests
import os
import time
import math

# this file must exist - created using getproducts.py
# file is updated to include the library discard metafield value for each product
# updated file can be used as input to listproducts.py to create report with library discard column
fn = 'products-all.json'

# don't commit secret to GitHub
ACCESS_TOKEN = 'FILLMEIN'

# returns library_discard metafield for this product
def get_library_discard_metafield(product_id):

    request = "https://friends-bookshop.myshopify.com/admin/api/2024-01/products/" + str(product_id) + "/metafields.json?namespace=custom&key=library_discard"
    headers = {'X-Shopify-Access-Token': ACCESS_TOKEN}

    response = requests.get(request,headers=headers)
    if response.status_code == 429:
        retry_after = 3 # default
        if 'retry-after' in response.headers:
            # shopify api returns retry-after header as a float e.g. 2.0
            # so round it up to nearest integer first since we want seconds
            retry_after = int(math.ceil(float(response.headers['retry-after'])))
        # retry once
        time.sleep(retry_after)
        response = requests.get(request,headers=headers)

    if response.status_code != 200:
        print('Error',response.status_code,'skipping product_id',product_id)
        return None
        
    metafields_json = response.json()

    return metafields_json['metafields']

products_with_libdiscard = []

# loop over products in input file, fetching metafields for each and appending to product json entry
with open(fn,encoding="utf-8") as f:
    j = json.loads(f.read())
    products = j['products']
    print('Reading from',fn)
    print('File contains',len(products),'products')

    n = 0
    for product in products:
        if 'metafields' in product:
            print('File already has metafields in it, aborting')
            n = 0
            break
        metafields = get_library_discard_metafield(product['id'])
        if metafields != None:
            product['metafields'] = metafields
            products_with_libdiscard.append(product)
            n += 1
        if n % 100 == 0:
            print('Fetched',n)  # progress indicator

    f.close()

n = len(products_with_libdiscard)
if n>0:
    print('Got metadata for',n,'products, writing to',fn)
    with open(fn,"w",encoding="utf-8") as out:
        # make a dictionary with one entry
        products = {'products':products_with_libdiscard}
        json.dump(products, out)
        out.close()