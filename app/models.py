from app.config import db


class User(db.Model):
    __tablename__ = "User"

    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(50),unique = True)
    login = db.Column(db.String(200),unique= True)
    password = db.Column(db.String(200),unique = True)
    admin = db.Column(db.Boolean())
    def __init__(self,public_id,login,password,admin):
        self.public_id = public_id
        self.login = login
        self.password = password
        self.admin = admin


class Note(db.Model):
    __tablename__ = "Notes"
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(200))
    content = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'),nullable = False)
    def __init__(self,title,content,user_id):
        self.title = title
        self.content = content
        self.user_id = user_id

