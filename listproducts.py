import json
from validatetags import get_shelf
from validatetags import is_gift_set
from validatetags import is_pot_pourri

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

    # ignore everything after first bracket, to handle e.g. Charles Dickens (Introduction by Rosalind Valland)
    if name.find('(')>0:
        name = name[:name.find('(')]       # items from the beginning through stop-1

    # last name is the last word
    words = name.split()
    ln = words[-1].strip()

    # ignore suffixes like MD and Jr.
    lastname_suffixes = {'Jr.','MD','M.D.','Ph.D','Ph.D.','PhD','III'}
    if ln in lastname_suffixes:
        # not gonna work if that's actually their last name, or their whole name, but deal with it if/when
        ln = words[-2].strip()

    # prefixes considered part of the last name
    lastname_prefixes = {'de','De','DE','du','Du','DU','El','la','La','LA','le','Le','LE','St.','van','Van','VAN','von','Von','VON'}

    prefixes_present = list(set(words).intersection(lastname_prefixes))
    if len(prefixes_present)>0:
        ln = prefixes_present[0] + ' ' + ln

    return ln

if False:
    assert lastname('John Hough Jr.') == 'Hough'
    assert lastname('Melvin Conner MD') == 'Conner'
    assert lastname('John le Carré') == 'le Carré'
    assert lastname('Charles Dickens (Introduction by Rolalind Valland)') == 'Dickens'
    assert lastname('Vincent van Gogh')== 'van Gogh'
    assert lastname('Cary Fagan, Banafsheh Erfanian')== 'Fagan'
    assert lastname('Megan Bradley (Editor), James Milner (Editor), Blair Peruniak (Editor)')== 'Bradley'
    assert lastname('William G. Thomas III') == 'Thomas'
    assert lastname('Rita Colwell PhD') == 'Colwell'

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
    published_at_date = 'N/A'   # happens if product is in draft status or not published because avail only in bundle
    if published_at:
        published_at_date = published_at[0:len('yyyy-mm-dd')]
    qty = int(variant['inventory_quantity'])
    price = variant['price']
    compareprice = variant['compare_at_price']
    if not compareprice or compareprice == '0.00':
        compareprice=''
    else:
        compareprice='$'+compareprice

    # show weight in grams
    weight = variant['weight']
    match variant['weight_unit']:
        case 'g':
            pass
        case 'kg':
            weight = variant['weight']*1000
        case _:
            print('Unsupported weight unit',variant['weight_unit'],'for id',id, ', expecting g or kg, aborting')
            assert(False)

    # metafields is added by getlibdiscard.py (expensive, therefore optional)
    lib_discard = 'Unknown'
    if 'metafields' in product:
        lib_discard = False
        for mf in product['metafields']:
            if mf['namespace'] == 'custom' and mf['key'] == 'library_discard':
                lib_discard = str(mf['value'])

    shelf = 'Unknown'
    if is_pot_pourri(id):
        shelf = 'Materials Management'
    else:
        shelf = get_shelf(tags)

    if is_gift_set(id) and skip_gift_sets:
        return 0

    if qty==0 and skip_sold_out_products:
        print('skipping sold-out',title)
        return 0

    s = str(id)+','+str(isbn)+',"'+title+'","'+author+'",'+author_lastname+',"'+tags+'",'+shelf+','\
        +published_at_date+','+str(qty)+','+price+','+compareprice+','+str(weight)+','+str(lib_discard)+'\n'
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

    with open(outfile,"w",encoding="utf-8") as out:
        n = 0
        #out.write('id,isbn,title,author,last name,tags,shelf,uploaded,qty,price,compareprice,weight in g'+'\n')
        out.write('id,isbn,title,author,last name,tags,shelf,uploaded,qty,price,compareprice,weight in g,library discard'+'\n')
        for product in products:
            n+=log_product(product,out)
        print('Wrote',n,'products to',outfile)
    out.close()
