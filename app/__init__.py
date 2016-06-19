from flask import Flask, render_template, g, session
from flask.ext.session import Session
from flask.ext.mongoengine import MongoEngine, MongoEngineSessionInterface
#from flask.ext.mongo_sessions import MongoDBSessionInterface
import os
import flask.ext.login as flask_login
from flask_bootstrap import Bootstrap
#from flask.ext.login import LoginManager


app = Flask(__name__)
app.config.from_object('config')
Session(app)
Bootstrap(app)
app.jinja_env.line_statement_prefix = '#'

db = MongoEngine(app)
app.session_interface = MongoEngineSessionInterface(db)
#db.init_app(app)
login_manager = flask_login.LoginManager()

login_manager.init_app(app)
login_manager.login_view = 'login'
#oid = OpenID(app, safe_roots=[], extension_responses=[pape.Response])
#oid = OpenID()
#oid.init_app(app)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

from app.mod_search.controllers import mod_search as search_module
from app.mod_search.controllers import mod_search_res as search_res_module
from app.mod_search.controllers import mod_annotate as annotate_module
from app.mod_search.controllers import mod_annotate2 as annotate_module2
from app.mod_search.controllers import mod_annotate3 as annotate_module3
from app.mod_search.controllers import mod_proxy as proxy_module
from app.mod_search.controllers import mod_js as js_module
from app.mod_search.controllers import mod_img as img_module
from app.mod_search.controllers import mod_login as login_module
from app.mod_search.controllers import mod_create_profile as create_profile_module
from app.mod_search.controllers import mod_profile as profile_module
from app.mod_search.controllers import mod_logout as logout_module
from app.mod_search.controllers import mod_index as index_module
from app.mod_search.controllers import mod_generate_token as generate_token_module
from app.mod_search.controllers import mod_task1 as task1_module
from app.mod_search.controllers import mod_task2 as task2_module
from app.mod_search.controllers import mod_sentiment as sentiment_module
from app.mod_search.controllers import mod_trustworthiness as trustworthiness_module
from app.mod_search.controllers import mod_all as all_module
from app.mod_search.controllers import mod_titles as titles_module
from app.mod_search.controllers import mod_sources as sources_module

app.register_blueprint(proxy_module)
app.register_blueprint(search_module)
app.register_blueprint(search_res_module)
app.register_blueprint(annotate_module)
app.register_blueprint(annotate_module2)
app.register_blueprint(annotate_module3)
app.register_blueprint(js_module)
app.register_blueprint(img_module)
app.register_blueprint(login_module)
app.register_blueprint(create_profile_module)
app.register_blueprint(profile_module)
app.register_blueprint(logout_module)
app.register_blueprint(index_module)
app.register_blueprint(generate_token_module)
app.register_blueprint(task1_module)
app.register_blueprint(task2_module)
app.register_blueprint(sentiment_module)
app.register_blueprint(trustworthiness_module)
app.register_blueprint(all_module)
app.register_blueprint(titles_module)
app.register_blueprint(sources_module)

