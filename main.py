"""`main` is the top level module for your Flask application."""

# Import the Flask Framework
import json
import os
import hashlib
import urllib2
import random
import logging
from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
#from flask_debugtoolbar import DebugToolbarExtension
from flask.wrappers import Response
from werkzeug.datastructures import MultiDict
from werkzeug.utils import secure_filename
from models import Phone
from models import Post
from models import Image
from google.appengine.api.datastore import Key

app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['SECRET_KEY'] = '123abcde'

#toolbar = DebugToolbarExtension(app)

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

    if request.method == 'POST':
        return render_template('sendmessage.html',sent=True)
    if request.method == 'GET':
        return responseMsg

@app.route('/sendmessage',methods=['POST','GET'])
def sendmessage():
    """
    phones = Phone.all()
    regIds = [phone.phone_id for phone in phones]
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
    """
    data = MultiDict()
    f = request.form
    for key in f.keys():
        data[key] = f[key]

    files = request.files.getlist('upload')

    titleMsgHash = data['title'] + data['post']# + chr(random.randrange(97,97+26+1))
    titleMsgHash = getHash(titleMsgHash)

    currentPost = Post(key_name=titleMsgHash,title=data['title'],msg=data['post'])
    currentPost.put()
    base64Strings = []
    i = 0
    for file in files:
        #file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        fileString = file.read()
        image64String = fileString.encode("base64")
        imageKeyName = data['title']+data['post']+'image'+str(i)
        tmpImage = Image(key_name=getHash(imageKeyName),encoded_string=image64String,post_id=currentPost.key())
        tmpImage.put()
        i = i+1

    logging.debug('reached end')
    return jsonify(data)

def getHash(text):
    return hashlib.md5(text).hexdigest()[:10]

@app.route('/posts/<postkey>')
def posts(postkey):
    p = Post.all()
    if postkey != 'all':
        key = Key(postkey)
        p.filter("__key__ =",key)
    postList = ['defualtfirst']
    for post in p.run():
        tmpPost = MultiDict()
        tmpPost['title'] = post.title
        tmpPost['msg'] = post.msg
        q = Image.all()
        q.filter("post_id",post.key())
        for i,image in enumerate(q.run()):
            tmpPost['image'+str(i)] = image.encoded_string
        postList.append(tmpPost)
    tmpOutput = MultiDict()
    tmpOutput['res'] = postList
    return jsonify(tmpOutput)

@app.route('/newphone',methods=['POST','GET'])
def newphone():
    if request.method == 'POST':
        json_obj = request.get_json(force=True)
        phone = Phone(key_name=json_obj['id'],phone_id = json_obj['id'],android_version = json_obj['android_version'])
        phone.put()
        """
        for thisPhone in allphones:
            if phone.phone_id == thisPhone.phone_id:
                exists = True
        if not exists:
            if not phone.is_saved():
                phone.put()
        """
        return 'db id is '
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
