from flask import Flask
from flask import request,make_response
from flask import render_template
from validatecsv import validate_csv
from validatecsv import imagesrc_list_from_csv

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
        try:
            results = validate_csv(csv_file)
        except Exception as e:
            results.append('Error reading csv file ' + csv_file.filename + ': ' + str(e))

        return make_response(render_template('validate-result.html',fn=csv_file.filename,results=results))

    # else GET, display the form
    return render_template('validate.html')

@app.route('/bookcovers',methods=["GET","POST"])
def bookcovers():
    if request.method == "POST":
        csv_file = request.files["csv_file"]
        imagelinks = []
        errormsg = ''
        try:
            imagelinks = imagesrc_list_from_csv(csv_file)
        except Exception as e:
            errormsg = 'Error reading csv file ' + csv_file.filename + ': ' + str(e)

        return make_response(render_template('covers-result.html',fn=csv_file.filename,results=imagelinks,errormsg=errormsg))

    # else GET, display the form
    return render_template('covers.html')
