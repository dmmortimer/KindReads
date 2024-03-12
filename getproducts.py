import json
import requests
import os

# outputs a giant json file of products
# file can be used as input to validatetags.py or listproducts.py
fn = 'products-all.json'

input_fn = 'products.txt'    # optional, if this file exists then only these products will be fetched

# don't commit secret to GitHub
ACCESS_TOKEN = 'FILLMEIN'
ACCESS_TOKEN = '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'

# returns all products
def get_all():

    request = "https://friends-bookshop.myshopify.com/admin/api/2023-04/products.json?limit=250&status=active&fields=id,tags,title,published_at,vendor,variants,images"
    headers = {'X-Shopify-Access-Token': ACCESS_TOKEN}

    all_products = []
    more = True
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

    return all_products

# fetches listed products
def fetch_ids(ids):

    request_prefix = "https://friends-bookshop.myshopify.com/admin/api/2023-04/products.json?fields=id,tags,title,published_at,vendor,variants,images"
    headers = {'X-Shopify-Access-Token': ACCESS_TOKEN}

    more_products = []

    ids_to_fetch = ''
    for id in ids:
        ids_to_fetch +=id+','   # trailing comma after last item doesn't seem to matter
    request = request_prefix + '&ids=' + ids_to_fetch

    print('Fetching',ids_to_fetch)
    response = requests.get(request,headers=headers)
    products_json = response.json()
    if response.status_code == 200:
        more_products = products_json['products']
    else:
        print('Oops, got error', response.status_code, ', unable to fetch products')
    return more_products

# returns products from list of product ids, one per line in file
# useful to add a tag to a specific list of books - fetch existing tags first then make a csv with new tag appended
def get_listed(fn):

    all_products = []

    batch_size = 10 # fetch in batches rather than one at a time, more efficient and avoid hitting rate limits

    with open(fn,encoding="utf-8") as f:

        ids = []

        for line in f:
            id = line.strip()
            ids.append(id)
            if len(ids) == batch_size:
                all_products += fetch_ids(ids)
                ids = []
                
        # fetch the last partial batch
        all_products += fetch_ids(ids)

    return all_products

all_products = []
if os.path.isfile(input_fn):
    print(input_fn,'is present, getting products listed by handle in file')
    all_products = get_listed(input_fn)
else:
    all_products = get_all()

#
print('Got',len(all_products),'products, writing to',fn)

# make a dictionary with one entry
products = {'products':all_products}

with open(fn, "w", encoding='utf-8') as f:
    json.dump(products, f)
    f.close()
