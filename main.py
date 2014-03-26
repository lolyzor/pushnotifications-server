"""`main` is the top level module for your Flask application."""

# Import the Flask Framework
import json
from flask import Flask
from flask import render_template
from flask import request
from models import Phone
from werkzeug.datastructures import MultiDict
import urllib2
from flask.wrappers import Response

app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return render_template('sendmessage.html',sent=False)


@app.route('/sendmessage2',methods=['POST','GET'])
def sendmessage2():
    dataToSend = dict()
    data = dict()
    phones = Phone.all()

    data['title'] = request.form['title'] or 'default title'
    data['post'] = request.form['post'] or 'defaul post'

    regIds = [phone.phone_id for phone in phones]
    dataToSend['registration_ids'] = regIds
    dataToSend['data'] = data

    headers = MultiDict()
    headers['Content-Type'] = 'application/json'
    headers['Authorization'] = "key=AIzaSyBsBuZuPlRkt45QstSJ_qaHC7_e1NFEIZU"
    req = urllib2.Request("https://android.googleapis.com/gcm/send", json.dumps(dataToSend), headers)
    f = urllib2.urlopen(req)
    responseMsg = f.read()
    f.close()
    #return responseMsg;
    #return json.dumps(dataToSend, sort_keys=True, indent=4)
    #return redirect(url_for('/'))
    return render_template('sendmessage.html',sent=True)

@app.route('/sendmessage',methods=['POST','GET'])
def sendmessage():
    phones = Phone.all()
    regIds = [phone.phone_id for phone in phones]
    #data = [{'title':'me'},{'post':'123'}]
    #dataToSend = [{'registration_ids':regIds},:data]
    data = dict()
    data['title'] = 'me'
    data['post'] = '123'
    dataToSend = dict()
    dataToSend['registration_ids'] = regIds
    dataToSend['data'] = data
    response = Response(json.dumps(dataToSend),mimetype='application/json')
    response.headers.add('Content-Type','application/json')
    response.headers.add('Authorization','key=AIzaSyBsBuZuPlRkt45QstSJ_qaHC7_e1NFEIZU')
    #return response

    headers = MultiDict()
    headers['Content-Type'] = 'application/json'
    headers['Authorization'] = "key=AIzaSyBsBuZuPlRkt45QstSJ_qaHC7_e1NFEIZU"
    req = urllib2.Request("https://android.googleapis.com/gcm/send", json.dumps(dataToSend), headers)
    f = urllib2.urlopen(req)
    responseMsg = f.read()
    f.close()
    return responseMsg;
    return json.dumps(dataToSend, sort_keys=True, indent=4)

@app.route('/newphone',methods=['POST','GET'])
def newphone():
    if request.method == 'POST':
        json_obj = request.get_json(force=True)
        phone = Phone(phone_id = json_obj['id'],android_version = json_obj['android_version'])
        allphones = Phone.all()
        exists = False
        for thisPhone in allphones:
            if phone.phone_id == thisPhone.phone_id:
                exists = True
        if not exists:
            phone.put()
    if request.method == 'GET':
        dbphones = Phone.all()
        return render_template('phones.html',phones=dbphones)

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def page_not_found(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
