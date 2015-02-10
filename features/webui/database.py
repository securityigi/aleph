from features.webui import app
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)
