import datetime
from flask import url_for
from app import db
import webhose
import datetime

class Sentiment(db.EmbeddedDocument):
	score = db.StringField(required=True)
	type = db.StringField(max_length=300, required=True)

class Emotion(db.EmbeddedDocument):
    joy = db.StringField(required=True)
    fear = db.StringField(required=True)
    anger = db.StringField(required=True)
    disgust = db.StringField(required=True)
    sadness = db.StringField(required=True)


class Objectivity(db.EmbeddedDocument):
    score = db.StringField(max_length=300, required=True)
		
class SearchItem(db.EmbeddedDocument):
	url = db.StringField(required=True)
	sentiment = db.EmbeddedDocumentField('Sentiment')
	objectivity = db.EmbeddedDocumentField('Objectivity')
	
class Search(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    query = db.StringField(default="vaccine")
    searchItems = db.ListField(db.EmbeddedDocumentField('SearchItem'))
    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at'],
        'ordering': ['-created_at']
    }

class QualityAssessment(db.Document):
    target = db.StringField(default="")
    overallQuality = db.StringField(default="1")
    accuracy = db.StringField(default="1")
    completeness = db.StringField(default="1")
    neutrality = db.StringField(default="1")
    relevance = db.StringField(default="1")
    trustworthiness = db.StringField(default="1")
    readability = db.StringField(default="1")
    precision = db.StringField(default="1")
    remarks = db.StringField(default="")
    timestamp = db.DateTimeField(default=datetime.datetime.now)

class NewQualityAssessment(db.Document):
    target = db.StringField(default="",required=True)
    overallQuality = db.StringField(default="1")
    accuracy = db.StringField(default="1")
    completeness = db.StringField(default="1")
    neutrality = db.StringField(default="1")
    relevance = db.StringField(default="1")
    trustworthiness = db.StringField(default="1")
    readability = db.StringField(default="1")
    precision = db.StringField(default="1")
    remarks = db.StringField(default="")
    timestamp = db.DateTimeField(default=datetime.datetime.now)


class User(db.Document):
    username = db.StringField()
    password = db.StringField()
    email = db.EmailField()
    doc_sequence = db.ReferenceField('Sequence')
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return unicode(self.id)
    
    '''def __init__(self, username, password, email):
        self.username = name
        self.email = email
        self.password = password'''

class Document(db.Document):
    url = db.StringField()
    title = db.StringField()
    snippet = db.StringField()
    sentiment = db.DecimalField()# db.EmbeddedDocumentField('Sentiment')
    emotion = db.DictField() #db.EmbeddedDocumentField('Emotion') #db.DictField()
    entities = db.ListField(db.DictField())
    trustworthiness = db.DecimalField()
    source = db.StringField()

class BestArticles(db.Document):
    user = db.ReferenceField('User')
    key = db.StringField()
    articles = db.ListField(db.StringField())
    discarted = db.ListField(db.StringField())
    timestamp = db.DateTimeField(default=datetime.datetime.now)

class Sequence(db.Document):
    sequence = db.ListField(db.ReferenceField('Document'))
    user = db.ReferenceField('User')