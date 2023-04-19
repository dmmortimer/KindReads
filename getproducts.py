import json
import requests

# outputs a giant json file of all products
# file can be used as input to validatetags.py or listproducts.py
fn = 'products-all.json'

# don't commit secret to GitHub
ACCESS_TOKEN = 'FILLMEIN'

request = "https://friends-bookshop.myshopify.com/admin/api/2023-04/products.json?limit=250&fields=id,tags,title,published_at,vendor,variants"
headers = {'X-Shopify-Access-Token': ACCESS_TOKEN}

more = True
all_products = []

# read it all in to memory and append to a giant list to be serialized to json
# maybe we should be processing it as we go but this is a convenient way to get a giant json file for other programs to use
# under 3000 titles is not that much anyway
while more:
    print('Fetching next 250')
    response = requests.get(request,headers=headers)
    products_json = response.json()
    more_products = products_json['products']
    all_products += more_products
    if 'next' in response.links:
        request = response.links['next']['url']
    else:
        more = False

#
print('Got',len(all_products),'products, writing to',fn)

# make a dictionary with one entry
products = {'products':all_products}

with open(fn, "w", encoding='utf-8') as f:
    json.dump(products, f)
    f.close()