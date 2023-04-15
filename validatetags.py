import json

# expects this file in local directory
fn = 'products-all.json'
skip_sold_out_products = True

# can get last 250 products without authentication or access token, from https://kindreads.com/products.json?limit=250
# can get first 250 (alphabetical) products from admin api like this on Windows
# curl -H "X-Shopify-Access-Token: FILLMEIN" "https://friends-bookshop.myshopify.com/admin/api/2023-04/products.json?limit=250&fields=id,tags,title,created_at,variants" > products-250.json
# or this on Linux
# curl -H 'X-Shopify-Access-Token: FILLMEIN' https://friends-bookshop.myshopify.com/admin/api/2023-04/products.json?limit=5 > products-5.json
# to get all products, use pagination, see getproducts.py. Writes to products-all.json

parent_tags = [
        'Fiction',
        'Kids',
        'Non-fiction',
        'Non-Fiction'
]

kids_age_tags = [
        'Board Books: Ages 0-3',
        'Board books: Ages 0-3',
        'board books: ages 0-3',
        'Middle Grade: Ages 8-12',
        'Middle grade: Ages 8-12',
        'Picture Books: Ages 3-8',
        'Picture books: Ages 3-8',
        'Teen'
]

# tags that need an accompanying collection tag
tags_in_collections = {
        'Fantasy':'Fantasy & Sci-Fi',
        'Science Fiction':'Fantasy & Sci-Fi',

        'Autobiography':'Memoirs and Biographies',
        'Biography':'Memoirs and Biographies',
        'Inspiring Bios':'Memoirs and Biographies',
        'Memoir':'Memoirs and Biographies',

        'Mystery':'Mystery and Thriller',
        'Psychological Thriller':'Mystery and Thriller',
        'Thriller':'Mystery and Thriller',

        # todo, change the rules so you can have history+fiction or politics+fiction without having the (non-fiction) politics and history collection tag?
        'History':'Politics and History',
        'Politics':'Politics and History'
}

known_tags = [
        'Academic',
        'Adventure',
        'Animals',
        'Arabic',
        'Astrology',
        'Autobiography',
        'Biography',
        'BIPOC',
        'Board Books: Ages 0-3',
        'Board books: Ages 0-3',
        'board books: ages 0-3',
        'Business',
        'Canadian',
        'Classic',
        'Clearance',
        'Contemporary',
        'Cookbook',
        'Crime',
        'Culture',
        'Economics',
        'Education',
        'Empowered Women',
        'Essays',
        'Family',
        'Fantasy',
        'Fantasy & Sci-Fi',
        'Fiction',
        'French',
        'Friendship',
        'Gift Card',
        'Graphic Novel',
        'Health',
        'Historical Fiction',
        'Historical fiction',
        'History',
        'Holiday',
        'Horror',
        'Horticulture',
        'Humor',
        'Indigenous',
        'Inspiring Bios',
        'International',
        'Kids',
        'LGBT',
        'Medicine',
        'Memoir',
        'Memoirs and Biographies',
        'Mental Health',
        'Middle Grade: Ages 8-12',
        'Middle grade: Ages 8-12',
        'Music',
        'Mystery',
        'Mystery and Thriller',
        'Non-fiction',
        'Non-Fiction',
        'Paranormal',
        'Parenting',
        'Philosophy',
        'Photography',
        'Picture books: Ages 3-8',
        'Picture Books: Ages 3-8',
        'Poetry',
        'Police',
        'Politics',
        'Politics and History',
        'Psychological Thriller',
        'Psychology',
        'Queer',
        'Religion',
        'Romance',
        'Science',
        'Science Fiction',
        'Self Help',
        'Self-Help',
        'Self-help',
        'Short Stories',
        'Sociology',
        'Spanish',
        'Sports',
        'Spy',
        'Staff Pick',
        'Staff pick',
        'staff pick',
        'Summer',
        'Technology',
        'Teen',
        'Thriller',
        'Travel',
        'True Crime',
        'War',
        'Writing'
]

# log error as csv line for importing into a spreadsheet
def log_error(isbn,title,tags,error_desc):
    print(isbn,',"',title,'","',tags,'",',error_desc,sep='')
    return

# validates tags and prints error messages
def validate_tags(product):
    isbn = product['id']
    tags = product['tags']
    tags_s = product['tags']
    title = product['title']
    created_at = product['created_at']

    available = None
    # public products.json looks like this
    if 'available' in product['variants'][0]:
        available = product['variants'][0]['available']
    else:
        # admin api json looks like this
        inventory_quantity = int(product['variants'][0]['inventory_quantity'])
        available = inventory_quantity>0

    if type(tags) != list:
        if len(tags) > 0:
            # admin api returns comma-separated list of tags, make it a list
            w_tags = tags.split(',')
            tags = []
            for tag in w_tags:
                tags.append(tag.strip())
        else:
            # no tags at all
            tags = []

    # Let's skip books not in inventory
    if not available and skip_sold_out_products:
        return

    # Rule: Must be at least one tag! To help categorize the product
    if len(tags) == 0:
        log_error(isbn,title,tags_s,'no tags')
        # stop here, no point going further
        return

    # Rule: Must be a known tag
    for tag in tags:
        if tag not in known_tags:
            log_error(isbn,title,tags_s,'unknown tag %s' % tag)

    # Rule: Must be exactly one parent tag
    n = len(set(tags).intersection(set(parent_tags)))
    if n == 0:
        log_error(isbn,title,tags_s,'missing parent tag')
    elif n>1 and 'Kids' not in tags:
        log_error(isbn,title,tags_s,'Adult book has %s parent tags' % n)
    elif n>2 and 'Kids' in tags:
        # Some kids books are marked fiction or nonfiction so allow 2 parent tags
        log_error(isbn,title,tags_s,'Kids book has %s parent tags' % n)

    # Rule: For Kids, must be at most one age tag
    if 'Kids' in tags:
        n = len(set(tags).intersection(set(kids_age_tags)))
        # pot-pourri and gift sets don't have an age group tag, so allow n == 0
        if n>1:
            log_error(isbn,title,tags_s,'has %s age group tags' % n)

    # Rule: for the combo collections, need consistent tags
    # Combo collections are defined to not show sold-out products and can only look at one tag to do this
    for tag in tags:
        if tag in tags_in_collections:
            if tags_in_collections[tag] not in tags:
                log_error(isbn,title,tags_s,'has tag %s but not the collection tag %s' % (tag,tags_in_collections[tag]))

with open(fn,encoding="utf-8") as f:
    j = json.loads(f.read())
    products = j['products']
    print('Reading from',fn)
    print('Validating tags for',len(products),'products')
    if skip_sold_out_products:
        print('Skipping sold-out products')
    else:
        print('Including sold-out products')
    print('isbn,title,tags,error',sep='')
    for product in products:
        validate_tags(product)
