from flask import Flask
from flask import request,make_response
from flask import render_template
from validatecsv import validate_csv
from validatecsv import imagesrc_list_from_csv
import os
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["DEBUG"] = True  # needed?

@app.route('/')
def mysite_page():
    return render_template('index.html')

@app.route('/validatecsv',methods=["GET","POST"])
def validatecsv():
    if request.method == "POST":
        csv_file = request.files["csv_file"]
        results = []
        decodedFileContent = None
        try:
            (results,decodedFileContent) = validate_csv(csv_file)
            # save the file in tmp directory - overwrites if already there
            # for possible reuse if user wants to view book covers for the same csv
            # will clean tmp directory periodically, manually or make a script todo
            # assume users won't interfere with each other
            # save decoded version of the file to avoid utf-8/latin-1 issues later
            saved_fn = secure_filename(csv_file.filename)
            saved_fn_path = os.path.join(tempfile.gettempdir(),saved_fn)
            decoded_csv_file = open(saved_fn_path, 'w')
            decoded_csv_file.write(decodedFileContent)
            decoded_csv_file.close()

        except Exception as e:
            results.append('Error reading csv file ' + csv_file.filename + ': ' + str(e))

        return make_response(render_template('validate-result.html',fn=saved_fn,results=results))

    # else GET, display the form
    return render_template('validate.html')

@app.route('/bookcovers/<fn>',methods=["GET","POST"])
@app.route('/bookcovers', defaults={'fn': None},methods=["GET","POST"])
def bookcovers(fn):
    if request.method == "POST":
        csv_file = request.files["csv_file"]
        imagelinks = []
        errormsg = ''
        try:
            imagelinks = imagesrc_list_from_csv(csv_file)
        except Exception as e:
            errormsg = 'Error reading csv file ' + csv_file.filename + ': ' + str(e)

        return make_response(render_template('covers-result.html',fn=csv_file.filename,results=imagelinks,errormsg=errormsg))

    # else GET, check if csv filename (previously uploaded during validatecsv) is present in URL
    # this is used for the "view book covers from this CSV" link on the validate csv results page
    if fn:
        full_fn = os.path.join(tempfile.gettempdir(), fn)
        imagelinks = []
        errormsg = ''
        try:
            csv_file = open(full_fn)
            imagelinks = imagesrc_list_from_csv(csv_file)
        except Exception as e:
            errormsg = 'Error reading previous csv file ' + fn + ': ' + str(e)

        return make_response(render_template('covers-result.html',fn=fn,results=imagelinks,errormsg=errormsg))

    # else display the form
    return render_template('covers.html')
