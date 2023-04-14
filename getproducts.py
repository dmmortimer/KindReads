# works from products.json in local directory
# can get last 250 products from https://kindreads.com/products.json?limit=250
# can't go higher than this without API
# todo - download complete list via API
import json

# age tags, used with Kids tag
# tags contained in collection tags (map tag -> collection tag) - if in first list, collection tag must be present
# option: automatically add the collection tag

# tbd: can Kids also have Fiction or Non-Fiction? Yes. But Kids overrules when choosing a shelf.
parent_tags = [
        'Fiction',
        'Kids',
        'Non-fiction',
        'Non-Fiction'
]

kids_age_tags = [
        'Board Books: Ages 0-3',    # should get rid of this tag
        'Board books: Ages 0-3',
        'board books: ages 0-3',
        'Middle Grade: Ages 8-12',
        'Middle grade: Ages 8-12',
        'Picture Books: Ages 3-8',
        'Picture books: Ages 3-8',
        'Teen'
]

# map of tags that need an accompanying collection tag
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
        'Board Books: Ages 0-3',    # should get rid of this tag
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
#'Self help',
'Self Help',
'Self-Help',
'Short Stories',
'Sociology',
'Spanish',
'Sports',
'Spy',
'Staff Pick',
'Summer',
'Technology',
'Teen',
'Thriller',
'Travel',
'True Crime',
'War',
'Writing'
]
# todo make the compare case insensitive (by upper-casing before compare)
# workaround: when there is a matching case, add it to the list above - helps make these visible

# later - a report that spits out the parent tag and optional age tag and optional collection tag and then other tags in a lump
# will be useful for the reconciliation
# later - report listing books sold with their parent tag etc - same report, qty 0 or non-0 indicates sold

# validates tags and prints error messages
def validate_tags(product):
    isbn = product['id']
    tags = product['tags']
    title = product['title']
    available = None
    # public products.json works like this
    if 'available' in product['variants'][0]:
        available = product['variants'][0]['available']
    else:
        # admin api json looks like this
        inventory_quantity = int(product['variants'][0]['inventory_quantity'])
        available = inventory_quantity>0

    if type(tags) != list:
        # admin api returns comma-separated list of tags, make it a list
        w_tags = tags.split(',')
        tags = []
        for tag in w_tags:
            tags.append(tag.strip())

    # Let's skip books not in inventory
    if not available:
        #print('Skipping sold-out',title)
        return

    # Rule: Must be a known tag
    for tag in tags:
        if tag not in known_tags:
            print('Error:',isbn,'has unknown tag"',tag,'"')

    # Rule: Must be exactly one parent tag
    n = len(set(tags).intersection(set(parent_tags)))
    if n == 0:
        print('Error:',isbn,'missing parent tag, expecting one of',parent_tags, 'got',tags)
    elif n>1 and 'Kids' not in tags:
        print('Error:',isbn,'has',n,'parent tags, for Adult expecting only one of',parent_tags,'got',tags)
    elif n>2 and 'Kids' in tags:
        print('Error:',isbn,'has',n,'parent tags, for Kids expecting at most one more of',parent_tags,'got',tags)

    # Rule: For Kids, must be at most one age tag
    if 'Kids' in tags:
        n = len(set(tags).intersection(set(kids_age_tags)))
        # pot-pourri doesn't have an age group tag, so allow n == 0
        if n>1:
            print('Error:',isbn,'has',n,'age group tags, expecting at most one of',kids_age_tags)


    # Rule: for the combo collections, need consistent tags
    for tag in tags:
        if tag in tags_in_collections:
            if tags_in_collections[tag] not in tags:
                print('Error:',isbn,'has tag',tag,'but not the collection tag',tags_in_collections[tag])

fn = 'products-250.json'
with open(fn) as f:
    j = json.loads(f.read())
    products = j['products']
    print('Reading from',fn)
    print('Validating tags for',len(products),'products')
    for product in products:
        validate_tags(product)
