import json
from validatetags import get_shelf

# expects this file in local directory
fn = 'products-all.json'
skip_sold_out_products = True
outfile = None
if skip_sold_out_products:
    outfile = 'products-in-stock.csv'
else:
    # might not work as expected, not paying much attention to the older qty=0 products
    outfile = 'products-all.csv'

# quick-and-dirty, treat last word as last name. not always correct.
# useful for locating books on fiction shelves which are stored alphabetically by author last name
def lastname(name):
    words = name.split()
    return words[-1].strip()

# log product as csv line for importing into a spreadsheet
# returns 0 if product skipped because no inventory, else returns 1
def log_product(product,out):
    isbn = product['id']
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
    qty = int(product['variants'][0]['inventory_quantity'])
    shelf = get_shelf(tags)

    if qty==0 and skip_sold_out_products:
        return 0

    s = str(isbn)+',"'+title+'","'+author+'",'+author_lastname+',"'+tags+'",'+shelf+','+published_at_date+','+str(qty)+'\n'
    out.write(s)

    return 1

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
        out.write('isbn,title,author,last name,tags,shelf,published_at,qty'+'\n')
        for product in products:
            n+=log_product(product,out)
        print('Wrote',n,'products to',outfile)
    out.close()
