from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# App & Database Initialization
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:pumpkinspice1928@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = "\xff&\xf9\x87\x81g\xa4'v$\xca\xaf\xea\xc0>\xb1\xfd\xb5;K\xab\xdbw\xbc"
db = SQLAlchemy(app)