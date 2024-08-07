import csv
from io import StringIO
from validatetags import validate_before_import


def validate_csv(csv_file):

    results_lines = []

    results_lines.append("Validating " + csv_file.filename + "\n")
    n=0
    num_with_errors = 0

    # needed to fix _csv.Error: iterator should return strings, not bytes (the file should be opened in text mode)
    # https://stackoverflow.com/questions/47828854/fileobject-passing-threw-csv-reader-python-3-6
    # https://www.reddit.com/r/cs50/comments/fwohlq/final_project_difficult_using_flask_request_and/

    # utf-8 doesn't work for CSVs from Val with these book titles, but latin-1 does
    # Más Allá del Invierno
    # I wish I could…Read!
    # The char … is definitely unicode (U+2026) so I'm not sure what's going on...
    # When I try these titles in a CSV, utf-8 decodes successfully
    # Perhaps Val's workflow saves the CSV with some other encoding

    fileContent = None
    try:
        fileContent = StringIO(csv_file.read().decode('utf-8'))
    except UnicodeDecodeError as e:
        # try again with latin-1
        print('decode '+csv_file.filename+' as utf-8 gives UnicodeDecodeError '+str(e)+', try again with latin-1')
        csv_file.seek(0)
        fileContent = StringIO(csv_file.read().decode('latin-1'))

    csvreader = csv.reader(fileContent,delimiter=',')

    # possible improvement, use header row to determine indexes instead of hard-coding them
    isbn_idx = 0    # Handle
    title_idx = 1   # Title
    author_idx = 3  # Vendor
    tags_idx = 5    # Tags
    price_idx = 13  # Variant Price
    compareprice_idx = 20   # Variant Compare At Price - obsolete, we stopped using in August 2024

    for row in csvreader:
        if row[isbn_idx] == 'Handle':
            # skip header line
            continue
        n+=1
        isbn = row[isbn_idx]
        title = row[title_idx]
        author = row[author_idx]
        tags = row[tags_idx]
        price = 0
        if row[price_idx] !='':
            price = float(row[price_idx].lstrip('$'))
        compareprice = 0
        # old code for compare-at price - we stopped using this in August 2024
        if False and row[compareprice_idx] !='':
            compareprice = float(row[compareprice_idx].lstrip('$'))
        errors = validate_before_import(tags,price,compareprice,title,author,isbn)
        if len(errors)>0:
            num_with_errors += 1
            for error in errors:
                results_lines.append('%s %s %s\n' % (isbn,title,error))

    if num_with_errors:
        results_lines.append( 'Validated %s items - %s had errors, printed above' % (n,num_with_errors))
    else:
        results_lines.append( 'Validated %s items, no errors found' % n)

    return (results_lines,fileContent.getvalue())

def imagesrc_list_from_csv(csv_file):

    imagesrc_list = []

    fileContent = None
    try:
        fileContent = StringIO(csv_file.read().decode('utf-8'))
    except AttributeError:
        # this happens when we're reading a saved temp file that was already decoded
        # try again without decoding
        csv_file.seek(0)
        fileContent = csv_file
    except UnicodeDecodeError as e:
        # try again with latin-1
        print('decode '+csv_file.filename+' as utf-8 gives UnicodeDecodeError '+str(e)+', try again with latin-1')
        csv_file.seek(0)
        fileContent = StringIO(csv_file.read().decode('latin-1'))

    csvreader = csv.reader(fileContent,delimiter=',')

    imagesrc_idx = 24   # default, unlikely to change? future-proof just in case
    for row in csvreader:
        if row[0] == 'Handle':
            # header row, find column that contains image src url
            try:
                imagesrc_idx = row.index('Image Src')
            except ValueError:
                # not there, that's strange, ignore and use the default
                continue
        else:
            imagesrc_list.append(row[imagesrc_idx])

    return imagesrc_list

