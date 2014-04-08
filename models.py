from google.appengine.ext import db


class Phone(db.Model):
    phone_id = db.StringProperty(required=True)
    android_version = db.StringProperty(required=False)

class Post(db.Model):
    title = db.StringProperty(required=True)
    msg = db.StringProperty(required=True)

class Image(db.Model):
    post_id = db.ReferenceProperty(Post)
    encoded_string = db.TextProperty(required=True)
