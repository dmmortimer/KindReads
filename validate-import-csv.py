# Run tag and other validation checks on a bulk import file before it's uploaded to Shopify
import csv
from validatetags import validate_before_import

fn = '2023-05-13-FOPLA-incomp-notfnd-book-profiles-scans_ONEtoCHECK.csv' # todo accept this from command-line
#fn = '2023-05-13-FOPLA-not_found-book-profiles-scans.csv'
#fn = '2023-05-13-FOPLA-complete-book-profiles-scans-dm.csv'

fn = 'Jordan/2023-05-12-FOPLA-not_found-book-profiles-scans - 2023-05-12-FOPLA-not_found-book-profiles-scans.csv'
#fn = 'Jordan/2023-05-12-FOPLA-incomplete-book-profiles-scans - 2023-05-12-FOPLA-incomplete-book-profiles-.csv'
#fn = 'Jordan/2023-05-12-FOPLA-complete-book-profiles-scans - 2023-05-12-FOPLA-complete-book-profiles-scans.csv'

print('Reading from',fn)
n=0
with open(fn,encoding="utf-8") as f:
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
        price = 0
        if row[19] !='':
            price = float(row[19])
        compareprice = 0
        if row[20] !='':
            compareprice = float(row[20])
        #print('Checking',isbn,title)
        errors = validate_before_import(tags,price,title)
        if len(errors)>0:
            for error in errors:
                print(isbn,title,error)
        if 0>price>=compareprice:
            print(isbn,title,'has price at or higher than compare price, this is unexpected')
        if compareprice>0 and compareprice<=8:
            print(isbn,title,'has compare-at price',compareprice,'less than $8, should be set to 0')

print('Validated',n,'items')