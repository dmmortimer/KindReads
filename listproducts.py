import json
from validatetags import get_shelf
from validatetags import is_gift_set

# expects this file in local directory
fn = 'products-all.json'
skip_sold_out_products = True
skip_gift_sets = True
outfile = None
if skip_sold_out_products:
    outfile = 'products-in-stock.csv'
else:
    # might not work as expected, not paying much attention to the older qty=0 products
    outfile = 'products-all.csv'

# quick-and-dirty, treat last word as last name. not always correct.
# useful for locating books on shelves which are stored alphabetically by author last name
def lastname(vendor):

    name = vendor

    # if a comma-separated list of authors, use the first one
    if vendor.find(',')>0:
        name = vendor[:vendor.find(',')]       # items from the beginning through stop-1

    words = name.split()
    ln = words[-1].strip()

    lastname_prefixes = {'le','la','de','du','Le','La','De','Du','LE','LA','DE','DU','van','Van','VAN'}

    prefixes_present = list(set(words).intersection(lastname_prefixes))
    if len(prefixes_present)>0:
        ln = prefixes_present[0] + ' ' + ln

    return ln

def log_variant(product,variant,out):
    id = product['id']
    isbn = variant['sku']
    if isbn == None:
        isbn = ''
    title = product['title']
    # problem in csv if title contains a double quote - cheat and remove it
    title = title.replace('"','')
    author = product['vendor']
    author_lastname = lastname(author)
    tags = product['tags']
    published_at = product['published_at']
    published_at_date = 'N/A'   # happens if product is in draft status
    if published_at:
        published_at_date = published_at[0:len('yyyy-mm-dd')]
    qty = int(variant['inventory_quantity'])
    price = variant['price']
    shelf = get_shelf(tags)

    if qty==0 and skip_sold_out_products:
        return 0

    if is_gift_set(id) and skip_gift_sets:
        return 0

    s = str(id)+','+str(isbn)+',"'+title+'","'+author+'",'+author_lastname+',"'+tags+'",'+shelf+','+published_at_date+','+str(qty)+','+price+'\n'
    out.write(s)
    return 1

# log product as csv line for importing into a spreadsheet
# returns 0 if product skipped because no inventory, else returns 1
def log_product(product,out):
    n = 0
    for variant in product['variants']:
        n += log_variant(product,variant,out)
    return n

with open(fn,encoding="utf-8") as f:
    j = json.loads(f.read())
    products = j['products']
    print('Reading from',fn)
    print('File contains',len(products),'products')
    if skip_sold_out_products:
        print('Skipping sold-out products')
    else:
        print('Including sold-out products')

    with open(outfile,"w",encoding="utf-8") as out:
        n = 0
        out.write('id,isbn,title,author,last name,tags,shelf,published_at,qty,price'+'\n')
        for product in products:
            n+=log_product(product,out)
        print('Wrote',n,'products to',outfile)
    out.close()
