from __future__ import print_function # In python 2.7

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, Response, send_from_directory, session, stream_with_context
from flask.ext.api.decorators import set_renderers
from flask.ext.api.renderers import HTMLRenderer
from flask.sessions import SessionInterface
from flask.ext.login import login_user , logout_user , current_user , login_required, LoginManager
import sys
import json
import call_alchemy_combined
import cchardet

from app import app, login_manager #, oid
from app.alchemyapi import AlchemyAPI
from BeautifulSoup import BeautifulSoup
import urllib2
import pandas as pd
import csv 
import numpy as np
import os
from sklearn.linear_model import SGDClassifier
from app.mod_search.forms import SearchForm, QualityForm, BestForm
from app.mod_search.models import Search, SearchItem, Sentiment, Objectivity, QualityAssessment, User, Document, NewQualityAssessment, Emotion, BestArticles, Sequence_old
import webhose
from sklearn.externals import joblib
MYDIR = os.path.dirname(__file__)
alchemyapi = AlchemyAPI()
import requests
import proxypy
from urlparse import urlparse
import datetime
import jwt
import random
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
import re
from urlparse import urlparse
from os.path import splitext
#import ast


reload(sys)
sys.setdefaultencoding('utf8')

webhose.config(token="b307005e-a773-4710-9aa8-98db353af657")

mod_search = Blueprint('search', __name__, url_prefix='')
mod_search_res = Blueprint('search_res', __name__, url_prefix='')
mod_annotate = Blueprint('annotate', __name__, url_prefix='')
mod_annotate2 = Blueprint('annotate2', __name__, url_prefix='')
mod_annotate3 = Blueprint('annotate3', __name__, url_prefix='')
mod_proxy = Blueprint('proxy', __name__, url_prefix='')
mod_js = Blueprint('js', __name__, url_prefix='')
mod_img = Blueprint('img', __name__, url_prefix='')
mod_login = Blueprint('login', __name__, url_prefix='')
mod_create_profile = Blueprint('create_profile', __name__, url_prefix='')
mod_profile = Blueprint('profile', __name__, url_prefix='')
mod_logout = Blueprint('logout', __name__, url_prefix='')
mod_index = Blueprint('index', __name__, url_prefix='')
mod_generate_token = Blueprint('generate_token', __name__, url_prefix='')
mod_task1 = Blueprint('task1', __name__, url_prefix='')
mod_task2 = Blueprint('task2', __name__, url_prefix='')
mod_land1 = Blueprint('land1',__name__,url_prefix='')
mod_land2 = Blueprint('land2',__name__,url_prefix='')
mod_sentiment = Blueprint('sentiment', __name__, url_prefix='')
mod_trustworthiness = Blueprint('trustworthiness', __name__, url_prefix='')
mod_entities = Blueprint('entities', __name__, url_prefix='')
mod_titles = Blueprint('titles', __name__, url_prefix='')
mod_sources = Blueprint('sources', __name__, url_prefix='')
mod_all = Blueprint('all', __name__, url_prefix='')


d = pd.read_csv(os.path.join(MYDIR,'feat.csv'),sep=";")
clf = joblib.load(os.path.join(MYDIR,'obj.pkl'))

# Replace these with your details
CONSUMER_KEY = 'yourconsumerkey'
CONSUMER_SECRET = 'yourconsumersecret'

# Only change this if you're sure you know what you're doing
CONSUMER_TTL = 86400

@mod_search.route('/generate_token/', methods=['GET', 'POST'])
@login_required
def generate_token():
    return jwt.encode({
                      'consumerKey': CONSUMER_KEY,
                      'userId': current_user.username,
                      'issuedAt': _now().isoformat() + 'Z',
                      'ttl': CONSUMER_TTL
                      }, CONSUMER_SECRET)

def _now():
    return datetime.datetime.utcnow().replace(microsecond=0)

'''@app.before_request
def before_request():
    #global session
    #session = app.session_interface.open_session(app,request)
    #session['s'] = None
    g.user = None
    if 'openid' in session:
        openid = session['openid']
        g.user = User.query.filter_by(openid=session['openid']).first()


@app.after_request
def after_request(response):
    #global session
    app.session_interface.save_session(app, session, response)
    return response'''

@mod_search.route('/search/', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm(request.form)
    s = None
    if form.validate():
        q = form.s.data
        session['q'] = q
        res = webhose.search(q)
        search_res = []
        for i in range(0,3):
            url = BeautifulSoup(urllib2.urlopen(res.posts[i].url).read()).head.find('meta', attrs={'http-equiv':'refresh'}).get("content")[7::]
            comb = call_alchemy_combined.call(url) #alchemyapi.combined("url",url)
            rs1 = comb['docSentiment'] if 'docSentiment' in comb else [] #alchemyapi.sentiment("url", url)
            rt1 = comb['taxonomy'] if 'taxonomy' in comb else []
            rr1 = comb['relations'] if 'relations' in comb else [] #alchemyapi.relations("url", url)
            rc1 = comb['concepts'] if 'concepts' in comb else []
            rk1 = comb['keywords'] if 'keywords' in comb else []
            re1 = comb['entities'] if 'entities' in comb else []
            em1 = comb['docEmotion'] if 'docEmotion' in comb else [] #alchemyapi.emotion("url", url)
            #if(rs1['status'] == "OK"):
            #if(rr1['status']== "OK"):
            if(comb['status'] == "OK"):
                for t in rr1:
                    if t['subject']['text']+"-"+t['action']['lemmatized']+("-"+t['object']['text'] if 'object' in t else "") in d:
                        d[t['subject']['text']+"-"+t['action']['lemmatized']+("-"+t['object']['text'] if 'object' in t else "")] = 1
                if 'sentiment' in d:
                    d['sentiment'] = rs1['score']
                for t in rt1:
                    if t['label'] in d:
                        d[t['label']] = t['score']
                for c in rc1:
                    if 'dbpedia' in rc1:
                        if c['dbpedia'] in d:
                            d[c['dbpedia']] = c['relevance']
                for k in rk1:
                    if k['text'] in k:
                        d[k['text']] = k['relevance']
                for e in re1:
                    if e['text'] in d:
                        d[e['text']] = e['relevance']
                for e in em1:
                    if e in d:
                        d[e] = emq[e]
            o = clf.predict(d)[0]
            sent = Sentiment(score=rs1['score'],type=rs1['type']) if rs1 is not None and len(rs1)>0 else Sentiment(score="0",type="")
            search_res.append(SearchItem(url=url,objectivity=Objectivity(score=str(o)),sentiment=sent))
        s = Search(query=q,searchItems=search_res)
        s.save()
        session['s'] = s
    else:
        session['s'] = None
    return render_template("search/search.html", form=form, search=session['s'])

@mod_search_res.route('/search_res/', methods=['GET', 'POST'])
@login_required
def search_res():
    form = QualityForm(request.form)
    if form.validate():
        q = QualityAssessment(user=current_user.to_dbref() ,target=session['u'],overallQuality=form.overallQuality.data,accuracy=form.accuracy.data,completeness=form.completeness.data,neutrality=form.neutrality.data,relevance=form.relevance.data,trustworthiness=form.trustworthiness.data,remarks=form.remarks.data)
        q.save()
    session['u'] = None
    if ('task2' in session and session['task2']==1):
        return redirect(url_for('task2'))
    return render_template("search/search.html", form=form, search=session['s'])


@mod_annotate.route('/annotate', methods=['GET', 'POST'])
@login_required
def annotate():
    url = "/proxy?headers=true&url="+request.args.get('url')
    form = QualityForm()
    return render_template("page4.html", url=url, target=request.args.get('url'),form=form)

@mod_annotate2.route('/annotate2/', methods=['GET', 'POST'])
def annotate2():
    form = QualityForm(request.form)
    q = None
    url = "/proxy?headers=true&url="+request.args.get('url')
    if form.validate():
        q = QualityAssessment(user=current_user.to_dbref(),
                              target=request.args.get('url'),
                              overallQuality=form.overallQuality.data,
                              accuracy=form.accuracy.data,
                              completeness=form.completeness.data,
                              neutrality=form.neutrality.data,
                              relevance=form.relevance.data,
                              trustworthiness=form.trustworthiness.data,
                              remarks=form.remarks.data,
                              precision=form.precision.data,
                              readability=form.readability.data)
        q.save()
        form.populate_obj(q)
    return render_template("page5.html", url=url, target=request.args.get('url'),form=form,qualityvalue=q)

@mod_annotate3.route('/annotate3', methods=['GET', 'POST'])
@login_required
def annotate3():
    url = "/proxy?headers=true&url="+request.args.get('url')
    form = QualityForm(request.form)
    if form.validate():
        q = QualityAssessment(user=current_user.to_dbref() ,target=session['u'],overallQuality=form.overallQuality.data,accuracy=form.accuracy.data,completeness=form.completeness.data,neutrality=form.neutrality.data,relevance=form.relevance.data,trustworthiness=form.trustworthiness.data,remarks=form.remarks.data)
        q.save()
    return render_template("page5.html", url=url, target=request.args.get('url'),form=form,qualityvalue=QualityAssessment)

@mod_js.route('/js/<path:path>')
def js(path):
    return send_from_directory(os.path.join(MYDIR, 'static', 'js'), path)

@mod_img.route('/img/<path:path>')
def get_image(path):
    if path.endswith(".png"):
        return send_from_directory(os.path.join(MYDIR, 'static', 'img'), path, mimetype='image/png')
    else:
        return send_from_directory(os.path.join(MYDIR, 'static', 'img'), path, mimetype='image/gif')

@mod_proxy.route('/proxy', methods=['GET', 'POST'])
@set_renderers(HTMLRenderer)
@login_required
def proxy():
    ann = "<script src=\"https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js\"></script><script language=\"javascript\" src=\"js/annotator.js\"></script><script language=\"javascript\">$( document ).ready(function() {var pageUri = function () {return {beforeAnnotationCreated: function (ann) {ann.uri = '%s';}};};\nvar app = new annotator.App();\napp.include(annotator.ui.main, {element: document.body , editorExtensions: [annotator.ui.tags.editorExtension]});\napp.include(annotator.storage.http, {prefix: 'https://limitless-refuge-57505.herokuapp.com'});\napp.include(annotator.identity.simple);\napp.include(pageUri);\napp.start().then(function(){app.annotations.load();}).then(function () { app.ident.identity = '%s'});});</script>" % (request.args.get('url'),request.args.get('url'),current_user.email)
    try:
        reply = json.loads(proxypy.get(request.query_string),'iso-8859-15')['content']
    except:
        reply = json.loads(proxypy.get(request.query_string),'latin-1')['content']
    #url = urlparse(request.args.get('url')).scheme + "://" + urlparse(request.args.get('url')).netloc
    url = urlparse(request.args.get('url')).scheme + "://"+urlparse(request.args.get('url')).netloc#+os.path.split(urlparse(request.args.get('url')).path)[0]
    #reply = reply.replace("src=\"/","src=\"%s/" % url)
    #reply = reply.replace("href=\"/","href=\"%s/" % url)
    if url[-1] != "/":
        url = url+"/"
            #reply = re.sub(r'src="((?!http:/))','src="' + url,reply)
#reply = re.sub(r'href="((?!http:/))','href="' + url,reply)
    reply = re.sub(r'src=\"((?!((www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,256}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)))(?!http(s)?:\/)(?!\/\/))','src="' + url,reply)
    
    reply = re.sub(r'href=\"((?!((www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,256}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)))(?!http(s)?:\/)(?!\/\/))','href="' + url,reply)
    reply = re.sub(r"src='((?!((www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,256}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)))(?!http(s)?:\/)(?!\/\/))","src='" + url,reply)
    
    reply = re.sub(r"href='((?!((www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,256}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)))(?!http(s)?:\/)(?!\/\/))","href='" + url,reply)
    #reply = re.sub(r'href=\'((?!http:/))','href=\'' + url,reply)
#reply = re.sub(r'((?<!http:)//)','/', reply)
#reply = reply.replace('https:/','https://')
    #reply = reply.replace("rel=\"stylesheet\" href=\"","rel=\"stylesheet\" href=\"%s" % url)
    #reply = reply.replace("rel=\"stylesheet\"  type=\"text/css\"  href=\"","rel=\"stylesheet\"  type=\"text/css\"  href=\"%s" % url)
    #reply = re.sub(r'href=\"((?!http:/))','href=\" + url,reply)
    #reply = reply.replace("href=\"/","href=\"%s" % url)
    #reply = re.sub("href=\"/","href=\"/",reply)
    reply = reply.replace("</head>","%s</head>" % ann)
    return render_template("page3.html", code=reply)

from flask.ext.login import login_user , logout_user , current_user , login_required

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    password = request.form['password']
    registered_user = User.objects(username=username,password=password).first()
    if registered_user is None:
        flash('Username or Password is invalid' , 'error')
        return redirect(url_for('login'))
    login_user(registered_user)
    session['user'] = registered_user
    flash('Logged in successfully')
    return redirect(request.args.get('next') or url_for('land1.land1'))

@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    user = User(request.form['username'] , request.form['password'],request.form['email'],Sequence_old.objects(__raw__={'user':{'$exists':False}}).first())
    user.save()
    s = user.doc_sequence
    s.user = user
    s.save()
    #db.session.add(user)
#db.session.commit()
    flash('User successfully registered')
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(id):
    return User.objects(pk=id).first()

#@app.route("/index")
#def logout():
#    render_template("index.html")

@mod_logout.route("/logout")
@login_required
def logout():
    user = current_user
    user.authenticated = False
    logout_user()
    return redirect(url_for('login'))


@mod_land2.route('/land2',methods=['GET','POST'])
@login_required
def land2():
    if len(session['docs'])==0:
        return render_template("done.html")
    form = BestForm(request.form)
    if form.validate() and request.args.get('k')!="no":
        b = BestArticles(key="all",articles = request.form.getlist('check'), discarted =[] , remarks=form.remarks.data, user = current_user.to_dbref() ) #<--- todo
        b.save()
    if request.args.get('url') is not None:
        form = QualityForm(request.form)
        if form.validate():
            q = NewQualityAssessment(user=current_user.to_dbref() ,target=request.args.get('url'),overallQuality=form.overallQuality.data,accuracy=form.accuracy.data,completeness=form.completeness.data,neutrality=form.neutrality.data,relevance=form.relevance.data,trustworthiness=form.trustworthiness.data,remarks=form.remarks.data,precision=form.precision.data,readability=form.readability.data) #add precision e readability
            q.save()
    return render_template("landing2.html")

@mod_task2.route('/task2',methods=['GET','POST'])
@login_required
def task2():
    try:
        u = session['docs'][0]
        session['u'] = u
        session['docs'] = session['docs'][1::]
        #u = session['docs'].pop()
        url = "/proxy?headers=true\&url="+u.url.replace("/annotate?url=","")
        form = QualityForm()
        return render_template("page4.html", url=url, target=u.url.replace("/annotate?url=",""),form=form)
    except Exception as e:
        return render_template("done.html", e=e)
#return render_template("page_index.html", docs=docs)



import urllib
@mod_task1.route('/task1',methods=['GET','POST'])
@login_required
def task1():
    form = BestForm(request.form)
    return render_template("entities.html",form=form, docs=session['docs'])

@mod_land1.route('/',methods=['GET','POST'])
@login_required
def land1():
    session['docs'] = current_user.doc_sequence.sequence
    return render_template("landing1.html")

@mod_trustworthiness.route('/trustworthiness',methods=['GET','POST'])
def trustworthiness():
    form = BestForm(request.form)
    if form.validate():
        b = BestArticles(key="sentiment",articles = request.form.getlist('check'), discarted =[] , remarks=form.remarks.data, user = current_user.to_dbref()) #<--- todo
        b.save()
    urls = [x.url for x in session['docs']]
    form.articles.choices = [(x,y) for x,y in enumerate(urls)]
    mapping = {x:y for x,y in enumerate(session['docs'])}
    d = session['docs']
    random.shuffle(d)
    return render_template("trustworthiness.html",form=form, doc=mapping, docs=d)

@mod_titles.route('/titles',methods=['GET','POST'])
def titles():
    form = BestForm(request.form)
    if form.validate():
        b = BestArticles(key="trustworthiness",articles = request.form.getlist('check'), discarted =[] , remarks=form.remarks.data, user = current_user.to_dbref() ) #<--- todo
        b.save()
    urls = [x.url for x in session['docs']]
    form.articles.choices = [(x,y) for x,y in enumerate(urls)]
    mapping = {x:y for x,y in enumerate(session['docs'])}
    d = session['docs']
    random.shuffle(d)
    return render_template("titles.html",form=form, doc=mapping, docs=d)

@mod_sources.route('/sources',methods=['GET','POST'])
def titles():
    form = BestForm(request.form)
    if form.validate():
        b = BestArticles(key="titles",articles = request.form.getlist('check'), discarted =[] , remarks=form.remarks.data, user = current_user.to_dbref() ) #<--- todo
        b.save()
    urls = [x.url for x in session['docs']]
    form.articles.choices = [(x,y) for x,y in enumerate(urls)]
    mapping = {x:y for x,y in enumerate(session['docs'])}
    d = session['docs']
    random.shuffle(d)
    return render_template("sources.html",form=form, doc=mapping, docs=d)

@mod_sentiment.route('/sentiment',methods=['GET','POST'])
def sentiment():
    form = BestForm(request.form)
    if form.validate():
        b = BestArticles(key="entities",articles = request.form.getlist('check'), discarted =[], remarks=form.remarks.data, user = current_user.to_dbref() ) #<--- todo
        b.save()
    urls = [x.url for x in session['docs']]
    form.articles.choices = [(x,y) for x,y in enumerate(urls)]
    mapping = {x:y for x,y in enumerate(session['docs'])}
    d = session['docs']
    random.shuffle(d)
    return render_template("sentiment.html",form=form, doc=mapping, docs=d)

@mod_all.route('/all',methods=['GET','POST'])
def all():
    form = BestForm(request.form)
    if form.validate():
        b = BestArticles(key="sources",articles = request.form.getlist('check'), discarted =[] , remarks=form.remarks.data, user = current_user.to_dbref() ) #<--- todo
        b.save()
    urls = [x.url for x in session['docs']]
    form.articles.choices = [(x,y) for x,y in enumerate(urls)]
    mapping = {x:y for x,y in enumerate(session['docs'])}
    d = session['docs']
    random.shuffle(d)
    return render_template("all.html",form=form, doc=mapping, docs=d)

def clean_html(html):
    """
        Copied from NLTK package.
        Remove HTML markup from the given string.
        
        :param html: the HTML string to be cleaned
        :type html: str
        :rtype: str
        """
    
    # First we remove inline JavaScript/CSS:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())
    # Then we remove html comments. This has to be done before removing regular
    # tags since comments can contain '>' characters.
    cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
    # Next we can remove the remaining tags:
    cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)
    # Finally, we deal with whitespace
    cleaned = re.sub(r"&nbsp;", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    return cleaned.strip()
