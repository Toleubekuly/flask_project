import uuid

from app import app
from flask_sqlalchemy import SQLAlchemy


app.config['SECRET_KEY'] = "SecretKey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Ertoshka0508@flask_db:5432/db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
db.init_app(app)
# app.config.from_object(Config)

# env = 'dev'
# if env == 'dev':
#     app.debug = True
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Ertoshka0508@localhost/test'
# else:
#     app.debug = False
#     app.config['SQLALCHEMY_DATABASE_URI'] = ''
#
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# with app.app_context():
#     db.create_all()

