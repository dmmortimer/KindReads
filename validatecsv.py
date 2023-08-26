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
            price = float(row[19].lstrip('$'))
        compareprice = 0
        if row[20] !='':
            compareprice = float(row[20].lstrip('$'))
        errors = validate_before_import(tags,price,compareprice,title,author,isbn)
        if len(errors)>0:
            num_with_errors += 1
            for error in errors:
                results_lines.append('%s %s %s\n' % (isbn,title,error))

    if num_with_errors:
        results_lines.append( 'Validated %s items - %s had errors, printed above' % (n,num_with_errors))
    else:
        results_lines.append( 'Validated %s items, no errors found' % n)

    return results_lines

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
    for row in csvreader:
        if row[0] == 'Handle':
            # skip header line
            # todo find column containing image src instead of hard-coding to 24
            continue
        imagesrc_list.append(row[24])

    return imagesrc_list

