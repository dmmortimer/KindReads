# Run tag and other validation checks on a bulk import file before it's uploaded to Shopify
import csv
from validatetags import validate_before_import

#fn = '2023-05-13-FOPLA-incomp-notfnd-book-profiles-scans_ONEtoCHECK.csv'
#fn = '2023-05-13-FOPLA-complete-book-profiles-scans - 2023-05-13-FOPLA-complete-book-profiles-scans.csv'
#fn = 'Jordan/2023-05-12-FOPLA-not_found-book-profiles-scans - 2023-05-12-FOPLA-not_found-book-profiles-scans.csv'
#fn = 'Jordan/2023-05-12-FOPLA-incomplete-book-profiles-scans - 2023-05-12-FOPLA-incomplete-book-profiles-.csv'
fn = 'Jordan/2023-05-12-FOPLA-complete-book-profiles-scans - 2023-05-12-FOPLA-complete-book-profiles-scans.csv'

# Write HTML file with all the book cover images for visual review
outfn = 'import-covers.html'

print('Reading from',fn)
n=0
with open(fn,encoding="utf-8") as f, \
    open(outfn,'w',encoding='utf-8') as f2:

    # crude! there must be a more elegant way but this works for now
    f2.write('<html>\n')
    f2.write('<head>\n')
    f2.write('<title>Book cover images</title>\n')
    f2.write('</head>\n')
    f2.write('<body>\n')

    csvreader = csv.reader(f,delimiter=',')
    for row in csvreader:
        if row[0] == 'Handle':
            # skip header line
            continue
        n+=1
        isbn = row[0]
        title = row[1]
        author = row[3]
        tags = row[5]
        imagesrc = row[24]
        price = 0
        if row[19] !='':
            price = float(row[19])
        compareprice = 0
        if row[20] !='':
            compareprice = float(row[20])
        #print('Checking',isbn,title)
        errors = validate_before_import(tags,price,compareprice,title)
        if len(errors)>0:
            for error in errors:
                print(isbn,title,error)
        
        f2.write('<img src="'+imagesrc+'">\n')

    # close out the html file
    f2.write('</body>\n')
    f2.write('</html>\n')

print('Validated',n,'items')
print('Generated',outfn,'which can be opened in a browser to review the book cover images')