import json

# expects this file in local directory
fn = 'products-all.json'
skip_sold_out_products = True

# can get last 250 products without authentication or access token, from https://kindreads.com/products.json?limit=250
# can get first 250 (alphabetical) products from admin api like this on Windows
# curl -H "X-Shopify-Access-Token: FILLMEIN" "https://friends-bookshop.myshopify.com/admin/api/2023-04/products.json?limit=250&fields=id,tags,title,published_at,variants" > products-250.json
# or this on Linux
# curl -H 'X-Shopify-Access-Token: FILLMEIN' https://friends-bookshop.myshopify.com/admin/api/2023-04/products.json?limit=5 > products-5.json
# to get all products, use pagination, see getproducts.py. Writes to products-all.json

nonfiction_tags = [
        'Non-fiction',
        'Non Fiction',
        'Non fiction',
        'Non-Fiction'
]
parent_tags = nonfiction_tags + [
        'Fiction',
        'Kids'
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

    shelf = 'Unknown'
    
    # Adult fiction
    if 'Fiction' in tags and 'Kids' not in tags:
        if 'French' in tags:
            shelf = 'French Fiction'
        else:
            shelf = 'Fiction'
    
    # Adult nonfiction
    if set(tags).intersection(set(nonfiction_tags)):
        if 'French' in tags:
            shelf = 'French Non-Fiction'
        else:
            shelf = 'Non-Fiction'
    
    # Cookbooks have a separate shelf
    if 'Cookbook' in tags:
        shelf = 'Cookbooks'
        # todo is there a separate shelf for French cookbooks?

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
                shelf = 'French Kids'
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
                shelf = 'Kids'

    return shelf
    
# validates tags and returns error messages or empty list
def validate_tags(product):
    tags = product['tags']
    tags_s = product['tags']

    errors = []

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
        return errors

    # Rule: Must be at least one tag! To help categorize the product
    if len(tags) == 0:
        errors.append('no tags')
        # stop here, no point going further
        return errors

    # Rule: Must be a known tag
    for tag in tags:
        if tag not in known_tags:
            errors.append('unknown tag %s' % tag)

    # Rule: Must be exactly one parent tag
    n = len(set(tags).intersection(set(parent_tags)))
    if n == 0:
        errors.append('missing parent tag')
    elif n>1 and 'Kids' not in tags:
        errors.append('Adult book has %s parent tags' % n)
    elif n>2 and 'Kids' in tags:
        # Some kids books are marked fiction or nonfiction so allow 2 parent tags
        errors.append('Kids book has %s parent tags' % n)

    # Rule: For Kids, must be at most one age tag
    if 'Kids' in tags:
        n = len(set(tags).intersection(set(kids_age_tags)))
        # pot-pourri and gift sets don't have an age group tag, so allow n == 0
        if n>1:
            errors.append('Kids book has %s age group tags' % n)

    # Rule: for the combo collections, need consistent tags
    # Combo collections are defined to not show sold-out products and can only look at one tag to do this
    for tag in tags:
        if tag in tags_in_collections:
            if tags_in_collections[tag] not in tags:
                errors.append('has tag %s but not the collection tag %s' % (tag,tags_in_collections[tag]))

    return errors

def main():
    with open(fn,encoding="utf-8") as f:
        j = json.loads(f.read())
        products = j['products']
        print('Reading from',fn)
        print('Validating tags for',len(products),'products')
        if skip_sold_out_products:
            print('Skipping sold-out products')
        else:
            print('Including sold-out products')
        print('isbn,title,tags,created_at,error',sep='')
        for product in products:
            errors = validate_tags(product)
            if len(errors)>0:
                for error in errors:
                    isbn = product['id']
                    tags_s = product['tags']
                    title = product['title']
                    published_at = product['published_at']
                    published_at_date = published_at[0:len('yyyy-mm-dd')]
                    # problem if title contains a double quote - cheat and remove it before printing
                    title = title.replace('"','')
                    print(isbn,',"',title,'","',tags_s,'",',published_at_date,',',error,sep='')

if __name__ == '__main__':
    main()