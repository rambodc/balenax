from __future__ import print_function
from flask import  Flask, jsonify, request, redirect,render_template, Response,url_for
from redis import Redis
import time 
import requests
import dClass
import gcpClass


app = Flask(__name__)
redis = Redis(host='redis', port=6379)

obj = dClass.dClass()
cloud = gcpClass.gcp()


@app.route('/')
def getdata():
    v = "Assembly Container RUnning , Now you can test Other containers using their End Points"
    #return v
    return render_template('index.html')

@app.route('/motor',methods = ['POST'])
def motor():
    global obj
    print('motor called :::')
    if request.method == 'POST':
        print('In post request')
        data = request.form['nm']
        _id = request.form['id']
        print('{}, {}'.format(data, _id))
        val = int(data)
        id = int(_id)
        obj.run_motor(val, id)
    return render_template('index.html')
    pass
@app.route('/test')
def test():
    print('In Assembly Container routing')
    r=requests.get('http://SensorContainer:5000')
    response = r.json()
    return 'Response from Sensor Container : {}'.format(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
