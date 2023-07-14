import csv
from io import StringIO
from validatetags import validate_before_import

# how to return exception? todo refactor to share this code
# not sure how to return either the rows or a useful error message to user
'''
def get_csv_rows(csv_file):
    return f
'''

def validate_csv(csv_file):

    results_lines = []

    results_lines.append("Validating " + csv_file.filename + "\n")
    n=0
    num_with_errors = 0

    # needed to fix _csv.Error: iterator should return strings, not bytes (the file should be opened in text mode)
    # https://stackoverflow.com/questions/47828854/fileobject-passing-threw-csv-reader-python-3-6
    # https://www.reddit.com/r/cs50/comments/fwohlq/final_project_difficult_using_flask_request_and/

    fileContent = StringIO(csv_file.read().decode('utf-8'))

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

    fileContent = StringIO(csv_file.read().decode('utf-8'))

    csvreader = csv.reader(fileContent,delimiter=',')
    for row in csvreader:
        if row[0] == 'Handle':
            # skip header line
            continue
        imagesrc_list.append(row[24])

    return imagesrc_list

