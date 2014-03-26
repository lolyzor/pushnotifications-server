from google.appengine.ext import db


class Phone(db.Model):
    phone_id = db.StringProperty(required=True)
    android_version = db.StringProperty(required=False)
