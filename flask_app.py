from flask import Flask
from flask import request,make_response
from flask import render_template
from validatecsv import validate_csv
from validatecsv import covers_from_csv

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/')
def mysite_page():
    return render_template('index.html')

@app.route('/validatecsv',methods=["GET","POST"])
def validatecsv():
    if request.method == "POST":
        csv_file = request.files["csv_file"]
        results = validate_csv(csv_file)
        response = make_response(results)
        response.headers["Content-Disposition"] = "attachment; filename=result.txt"
        return response
    # else GET, display the form
    return render_template('validate.html')

@app.route('/bookcovers',methods=["GET","POST"])
def bookcovers():
    if request.method == "POST":
        csv_file = request.files["csv_file"]
        results = covers_from_csv(csv_file)
        response = make_response(results)
        response.headers["Content-Disposition"] = "attachment; filename=covers.html"
        return response
    # else GET, display the form
    return render_template('covers.html')