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
        try:
            results = validate_csv(csv_file)
            return make_response(render_template('validate-result.html',results=results))
        except UnicodeDecodeError as e:
            return make_response('Error decoding csv file: '+str(e))
        except ValueError as e:
            return make_response('Error reading csv file: '+str(e))

    # else GET, display the form
    return render_template('validate.html')

@app.route('/bookcovers',methods=["GET","POST"])
def bookcovers():
    if request.method == "POST":
        csv_file = request.files["csv_file"]
        try:
            imagelinks = imagesrc_list_from_csv(csv_file)
            return make_response(render_template('covers-result.html',results=imagelinks))
        except UnicodeDecodeError as e:
            return make_response('Error decoding csv file: '+str(e))

    # else GET, display the form
    return render_template('covers.html')
