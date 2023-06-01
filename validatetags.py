import json
import math
import re

# expects this file in local directory
fn = 'products-all.json'
skip_sold_out_products = True

# Write HTML file with all the book cover images for visual review
write_covers_html = True
outfn = 'covers.html'

# get first 250 (alphabetical) products from admin api like this on Windows
# curl -H "X-Shopify-Access-Token: FILLMEIN" "https://friends-bookshop.myshopify.com/admin/api/2023-04/products.json?limit=250&fields=id,tags,title,published_at,variants" > products-250.json
# or this on Linux
# curl -H 'X-Shopify-Access-Token: FILLMEIN' https://friends-bookshop.myshopify.com/admin/api/2023-04/products.json?limit=5 > products-5.json
# to get all products, use pagination, see getproducts.py. Writes to products-all.json

# products that are not books, can be useful to skip these for reporting
# todo could improve this by using product category or type, or even tags, and not have hard-coded list of product ids
gift_sets = [
    7798515499159,  # Children's Surprise Box of Books
    7286971564183,  # Christmas Gift Card
    5672176124055,  # Don't feel like choosing? A Surprise Box of Books is for you!
    7286938042519,  # Gratitude Gift Card
    7286983229591,  # Happy Holidays Gift Card
    7281284055191,  # Secret Santa Gift Card
    7240056537239   # Kids Advent Calendar Gift Set (12 or 24 Books)
]

pot_pourri = [
    7988045938839,  # Pot-Pourri 2015
    7326988370071,  # Pot-Pourri 2021
    7869301096599   # Pot-Pourri 2022
]

# Sets/collections that have been checked in Room 149 and we have all the books in the set
# If we don't have all books, the words set or collection need to be removed from the title
confirmed_sets_or_false_positives = [
    7176181088407,  # Bedtime (Baxter Bear Collection)
    7176181022871,  # Dinnertime (Baxter Bear Collection)
    7974125633687,  # Disney's: Winnie the Pooh Storybook Collection (Disney Storybook Collections)
    6579553173655,  # Learn and Grow on the Go! (Nick Jr. Carry-along Boxed Set)
    7855282847895   # Yasmina Series (Set of 4 Books) Arabic سلسلة ياسمينة
]


# Price guidelines
min_price = 0.99
max_price = 20
min_compare_price = 5.99    # Pricing guide says 8.00 but need to confirm with Aida. For now, use 5.99 so no failed validations
# beware, uses product handle (id) as key, not isbn
# all Classic books bypass the max price check, no need to list as exceptions
price_exceptions = {
    '7949689258135': 99.99,     # Angel Illyria Haunted
    '7949689520279': 69.00,     # Spike: Into the Light
    '7949689979031': 59.99,     # Trinity: The Man of Steel, The Dark Knight, The Amazing Amazon (3 Volumes)
    '8008024850583': 39.99,     # Angel and Faith: Season Ten Volume 1: Where the River Meets the Sea (Angel & Faith)
    '8008025145495': 49.99,     # Angel and Faith: Season Ten Volume 3 - United
    '8008024883351': 44.99,     # Buffy: Season Ten Volume 3 Love Dares You (Buffy the Vampire Slayer)
    '8010714841239': 99.99      # Sex by Madonna
}

def is_gift_set(id):
    return id in gift_sets

def is_pot_pourri(id):
    return id in pot_pourri

nonfiction_tags = [
        'Non-fiction',
        'Non Fiction',
        'Non fiction',
        'Non-Fiction'
]
parent_tags = nonfiction_tags + [
        'Fiction',
        'Kids',
        'Poetry'
]

kids_board_tags = [
        'Board Books: Ages 0-3',
        'Board books: Ages 0-3',
        'board books: ages 0-3'
]
kids_picture_tags = [
        'Picture Books: Ages 3-8',
        'Picture books: Ages 3-8'
]
kids_middle_tags = [
        'Middle Grade: Ages 8-12',
        'Middle grade: Ages 8-12'
]
teen_tags = ['Teen']

kids_age_tags = kids_board_tags + kids_picture_tags + kids_middle_tags + teen_tags

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
        'Art',
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
        'crime',
        'Culture',
        'Economics',
        'Education',
        'Empowered Women',
        'Environment',
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
        'Non Fiction',
        'Non fiction',
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
        'Portuguese',
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

# list not used, this is just for reference and matches shelves as at April 2023
shelves = [
    'Fiction',
    'Non-Fiction',
    'French Fiction',
    'French Non-Fiction',
    'Kids Board Books',
    'Kids Picture Books',
    'Kids Middle Grade',
    'Teen',
    'French Kids Board Books',
    'French Kids Picture Books',
    'French Kids Middle Grade',
    'French Teen',
    'Cookbooks',
    'Folio Society/Vintage',
    'Kids Speciality',
    'Seasonal',
    'Sets and Anthologies'
]

# best guess as to which shelf the book will be on
def get_shelf(tags):

    if len(tags) > 0:
        # admin api returns comma-separated list of tags, make it a list
        w_tags = tags.split(',')
        tags = []
        for tag in w_tags:
            tags.append(tag.strip())
    else:
        # no tags at all
        tags = []

    shelf = 'Unknown'
    
    if 'Classic' in tags:
        # Not always correct, some books tagged Classic are in regular Fiction/Non-Fiction sections
        # Perhaps we need a specific Folio Society tag
        shelf = 'Folio Society/Vintage'
        return shelf

    # Adult fiction
    if 'Fiction' in tags and 'Kids' not in tags:
        if 'French' in tags:
            shelf = 'French Fiction'
        else:
            shelf = 'Fiction'
    
    # Graphic novels
    if 'Graphic Novel' in tags:
        if 'French' in tags:
            shelf = 'Bande Dessinée'
        else:
            shelf = 'Graphic Novels'

    # Adult nonfiction
    if set(tags).intersection(set(nonfiction_tags)):
        if 'French' in tags:
            shelf = 'French Non-Fiction'
        else:
            shelf = 'Non-Fiction'
    
    # English Cookbooks have a separate shelf
    if 'Cookbook' in tags:
        if 'French' in tags:
            shelf = 'French Non-Fiction'
        else:
            shelf = 'Cookbooks'

    # Poetry is shelved with nonfiction, but Kids overrides
    if 'Poetry' in tags:
        if 'French' in tags:
            shelf = 'French Non-Fiction'
        else:
            shelf = 'Non-Fiction'

    # Kids
    if 'Kids' in tags:
        if 'French' in tags:
            if set(tags).intersection(set(kids_board_tags)):
                shelf = 'French Kids Board'
            elif set(tags).intersection(set(kids_picture_tags)):
                shelf = 'French Kids Picture'
            elif set(tags).intersection(set(kids_middle_tags)):
                shelf = 'French Kids Middle Grades'
            elif set(tags).intersection(set(teen_tags)):
                shelf = 'French Teen'
            else:
                shelf = 'French Kids Missing Age Tag'
        else:
            if set(tags).intersection(set(kids_board_tags)):
                shelf = 'Kids Board'
            elif set(tags).intersection(set(kids_picture_tags)):
                shelf = 'Kids Picture'
            elif set(tags).intersection(set(kids_middle_tags)):
                shelf = 'Kids Middle Grades'
            elif set(tags).intersection(set(teen_tags)):
                shelf = 'Teen'
            else:
                shelf = 'Kids Missing Age Tag'

    return shelf
    
def validate_before_import(tags,price,compareprice,title):
    # hack let's make a fake product
    product = {}
    product['tags'] = tags
    product['id'] = 1   # dummy value
    product['title'] = title
    product['variants'] = []
    product['variants'].append({})
    product['variants'][0]['inventory_quantity'] = 1
    product['variants'][0]['price'] = price
    product['variants'][0]['compare_at_price'] = compareprice
    return validate_tags(product)

# validates tags and returns error messages or empty list
# new: also validates prices
# new: also checks if title contains set or collection and is not on exception list
# new: also checks that the product is set to require shipping - we don't sell digital products on the site
# todo - refactor as this is now misnamed
def validate_tags(product):
    tags = product['tags']
    id = product['id']
    title = product['title']

    errors = []

    inventory_quantity = int(product['variants'][0]['inventory_quantity'])
    available = inventory_quantity>0

    if len(tags) > 0:
        # convert comma-separated list of tags into a list
        w_tags = tags.split(',')
        tags = []
        for tag in w_tags:
            tags.append(tag.strip())
    else:
        # no tags at all
        tags = []

    # Let's skip books not in inventory
    if not available and skip_sold_out_products:
        return errors

    # This must be set for orders to get fulfilled correctly
    requires_shipping = product['variants'][0]['requires_shipping']
    if not requires_shipping:
        errors.append('shipping incorrectly configured as a digital product instead of physical product')

    # Rule: Must be at least one tag! To help categorize the product
    if len(tags) == 0:
        # Gift sets are an exception, don't need tags
        if not is_gift_set(id):
            errors.append('no tags')
    else:
        # Rule: Must be a known tag
        for tag in tags:
            if tag not in known_tags:
                errors.append('unknown tag %s' % tag)

        # Rule: Must be exactly one parent tag
        n = len(set(tags).intersection(set(parent_tags)))
        if n == 0:
            errors.append('missing parent tag')

        # Exception: Pot-Pourri can have multiple parent tags e.g. F, NF, Poetry
        if is_pot_pourri(id):
            pass
        elif n>1 and 'Kids' not in tags:
            errors.append('Adult book has %s parent tags' % n)
        elif n>2 and 'Kids' in tags:
            # Some kids books are marked fiction or nonfiction as well so allow 2 parent tags
            errors.append('Kids book has %s parent tags' % n)

        # Rule: For Kids, must be exactly one age tag
        if 'Kids' in tags:
            n = len(set(tags).intersection(set(kids_age_tags)))
            # Exception: Pot-Pourri doesn't need an age group tag
            # Exception: Gift sets don't need tags
            if n != 1 and not is_gift_set(id) and not is_pot_pourri(id):
                errors.append('Kids book has %s age group tags' % n)

        # Rule: for the combo collections, need consistent tags
        # Combo collections are defined to not show sold-out products and can only look at one tag to do this
        for tag in tags:
            if tag in tags_in_collections:
                if tags_in_collections[tag] not in tags:
                    errors.append('has tag %s but not the collection tag %s' % (tag,tags_in_collections[tag]))

    # Titles that indicate sets or collections are checked in Room 149 to make sure we have the entire set not just one volume
    title_words = re.split(r'\W+',title.lower())
    if 'set' in title_words  or 'collection' in title_words:
        if id not in confirmed_sets_or_false_positives and id not in gift_sets:
            errors.append('has a title suggesting a set or collection but is not on list of confirmed sets or false positives')

    # price check, for first variant
    price = float(product['variants'][0]['price'])
    compareprice = 0
    if 'compare_at_price' in product['variants'][0]:
        compareprice = product['variants'][0]['compare_at_price']
        if compareprice:
            compareprice = float(product['variants'][0]['compare_at_price'])
        else:
            compareprice = 0

    # If product is on price exceptions list, no further checks needed (it should follow the $X.99 convention but this isn't checked)
    id_s = str(id)
    if id_s in price_exceptions:
        price_exception = price_exceptions[id_s]
        if price != price_exception:
            errors.append('has price %s not matching expected price %s. To change expected price, update the validation script.' % (price,price_exception))
        return errors   # I don't love this return statement, should refactor

    # Check for unusually low price
    if price < min_price:
        errors.append('has price %s below minimum expected price %s' % (price,min_price))

    # Check for unusually high price
    elif price > max_price:
        # Gift sets can be more expensive, don't check them
        if id not in gift_sets:
            # Classic can have any price
            if 'Classic' not in tags:
                errors.append('has price %s above maximum price %s' % (price,max_price))

    # All prices end in $X.99
    cents = round(price - math.floor(price),2)
    if cents != 0.99:
        # Pot-Pourri doesn't follow $X.99 convention, nor do gift sets
        if id not in pot_pourri and not is_gift_set(id):
            errors.append('has price %s not ending in .99 counter to our pricing guidelines' % (price))

    # compare-at price should be higher than price (although Shopify will ignore it if it is)
    if 0>price>=compareprice:
        errors.append('has price at or higher than compare price, this is unexpected')

    # If a book is priced at $8 or less dollars, leave the “Compare at” column empty
    if compareprice>0 and compareprice<min_compare_price:
        errors.append('has compare-at price %s less than %s, leave blank or set to 0 per our pricing guidelines' % (compareprice, min_compare_price))

    return errors

def main():

    if write_covers_html:
        f2 = open(outfn,'w',encoding='utf-8')

    with open(fn,encoding="utf-8") as f:

        if write_covers_html:
            # crude! there must be a more elegant way but this works for now
            f2.write('<html>\n')
            f2.write('<head>\n')
            f2.write('<title>Book cover images</title>\n')
            f2.write('</head>\n')
            f2.write('<body>\n')

        j = json.loads(f.read())
        products = j['products']
        print('Reading from',fn)
        print('Validating tags for',len(products),'products')
        if skip_sold_out_products:
            print('Skipping sold-out products')
        else:
            print('Including sold-out products')
        print('id,isbn,title,tags,created_at,error',sep='')
        for product in products:
            isbn = product['variants'][0]['sku']
            if isbn == None:
                isbn = ''

            errors = validate_tags(product)
            if len(errors)>0:
                for error in errors:
                    id = product['id']
                    tags_s = product['tags']
                    title = product['title']
                    published_at = product['published_at']
                    published_at_date = 'N/A'   # happens if product is in draft status
                    if published_at:
                        published_at_date = published_at[0:len('yyyy-mm-dd')]
                    # problem if title contains a double quote - cheat and remove it before printing
                    title = title.replace('"','')
                    print(id,',',isbn,',"',title,'","',tags_s,'",',published_at_date,',',error,sep='')

            if write_covers_html:
                # todo refactor as this is now checked multiple places
                inventory_quantity = int(product['variants'][0]['inventory_quantity'])
                include = inventory_quantity>0 or not skip_sold_out_products
                if include:
                    image = product['images'][0]
                    width = int(image['width'])
                    height = int(image['height'])
                    imageurl = image['src']
                    img = '<img src="'+imageurl+'"'
                    if height>500:
                        # scale down the really large images
                        img += ' height=500'
                    img += '>'
                    # todo make it a hyperlink to the product on the store
                    '''
                    storelink = 'https://kindreads.com/products/'+
                        <a href="link address"><img src="image destination"></a>
                    '''
                    f2.write(img+'\n')

    if write_covers_html:
        # close out the html file
        f2.write('</body>\n')
        f2.write('</html>\n')
        print('Generated',outfn,'which can be opened in a browser to review the book cover images')

    print_known_tags = False
    if print_known_tags:
        for tag in known_tags:
            print(tag)
        
if __name__ == '__main__':
    main()