import json
import requests
from validatetags import get_shelf
import time

fn = 'orderitems.csv'

# don't commit secret to GitHub
ACCESS_TOKEN = 'FILLMEIN'

# this is an expensive operation
# todo consider fetching tags for multiple products in one call
def get_tags(product_id):
    request = "https://friends-bookshop.myshopify.com/admin/api/2023-04/products/"+str(product_id)+".json?fields=tags,title"
    headers = {'X-Shopify-Access-Token': ACCESS_TOKEN}
    response = requests.get(request,headers=headers)
    product_json = response.json()
    tags = product_json['product']['tags']
    return tags

def log_order_line_items(f,order):
    order_number = order['order_number']
    created_at = order['created_at']
    created_at_date = created_at[0:len('yyyy-mm-dd')]
    line_items = order['line_items']
    for line_item in line_items:
        isbn = line_item['sku']
        title = line_item['title']
        # problem if title contains a double quote - cheat and remove it before printing
        title = title.replace('"','')
        author=line_item['vendor']
        price=line_item['price']
        tags = None
        if line_item['product_exists']:
            print('Fetching tags for',title)
            tags=get_tags(line_item['product_id'])
        else:
            print('Tags not available for',title,'because product has changed since order')
            tags = 'n/a due to product changes after order'
        shelf=get_shelf(tags)
        s = str(order_number)+','+created_at_date+','+str(isbn)+',"'+title+'","'+author+'",'+price+',"'+tags+'",'+shelf+'\n'
        f.write(s)
        # Exceeded 2 calls per second for api client. Reduce request rates to resume uninterrupted service.
        time.sleep(600/1000)    # sleep 600 milliseconds
    return

num_orders=0
more = True

limit=250
request = "https://friends-bookshop.myshopify.com/admin/api/2023-04/orders.json?status=any&fields=order_number,created_at,line_items&limit="+str(limit)
#request = "https://friends-bookshop.myshopify.com/admin/api/2023-04/orders.json?status=any&created_at_max=2022-01-11&fields=order_number,created_at,line_items&limit="+str(limit)
headers = {'X-Shopify-Access-Token': ACCESS_TOKEN}

with open(fn, "w", encoding='utf-8') as f:

    f.write('order_number,created_at,isbn,title,author,price,tags,shelf\n')
    while more:
        print('Fetching next',limit)
        response = requests.get(request,headers=headers)
        orders_json = response.json()
        orders = orders_json['orders']
        for order in orders:
            # this is slow, fetching each book one at a time, consider using products.json with a list of IDs
            log_order_line_items(f,order)
            num_orders+=1
        if True and 'next' in response.links:
            request = response.links['next']['url']
        else:
            more = False

print('Got',num_orders,'orders, written to',fn)