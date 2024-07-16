from flask import Flask, render_template, request, jsonify, make_response
from app import app
from app.config import db
from app.models import User,Note
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from app.auth import token_required

@app.route('/')
@app.route('/login')
def Login():
    data = request.authorization
    if not data or not data.username or not data.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    user_data = User.query.filter_by(login = data.username).first()
    if not user_data:
        return make_response("Could not find this login" , 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
    if check_password_hash(user_data.password,data.password):
        token = jwt.encode({'public_id' : user_data.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},app.config['SECRET_KEY'])
        return jsonify({'token' : token})
    return make_response("Invalid password" , 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

@app.route('/user',methods = ['POST'])
@token_required
def createUser(current_user):
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})
    data = request.get_json()
    hashed_password = generate_password_hash(str(data['password']), method = 'pbkdf2:sha256')
    user = User(public_id = str(uuid.uuid4()), login= data['login'],password= hashed_password,admin= False)
    db.session.add(user)
    db.session.commit()
    return "New user created"


@app.route('/user',methods = ['GET'])
@token_required
def getAll(current_user):
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})

    data = User.query.all()
    output = []
    for i in data:
        dict = {}
        dict['public_id'] = i.public_id
        dict['login'] = i.login
        dict['password'] = i.password
        dict['admin'] = i.admin
        output.append(dict)
    return jsonify({"user" : output})

@app.route('/user/<public_id>',methods = ['GET'])
@token_required
def getOne(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})

    user = User.query.filter_by(public_id = public_id).first()
    if not user:
        return jsonify({'Message' : 'No user'})
    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['login'] = user.login
    user_data['password'] = user.password
    user_data['admin'] = user.admin
    return jsonify({'User':user_data})

@app.route('/user/<public_id>',methods = ['POST'])
@token_required
def promoteUser(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})

    user = User.query.filter_by(public_id = public_id).first()
    if not user:
        return jsonify({'Message' : 'No user'})
    user.admin = True
    db.session.commit()
    return jsonify({'Message':'User has been promoted'})

@app.route('/user/<public_id>',methods = ['DELETE'])
@token_required
def deleteUser(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'})

    user = User.query.filter_by(public_id = public_id).first()
    if not user:
        return jsonify({'Message' : 'No user'})
    User.query.filter_by(public_id = public_id).delete()
    db.session.commit()
    return jsonify({"Message":"User has been deleted"})

@app.route('/user/<public_id>',methods = ['PUT'])
@token_required
def updateUser(current_user, public_id):
    user = User.query.filter_by(public_id = public_id).first()
    if not user:
        return jsonify({'Message' : 'No user'})
    data = request.get_json()
    if 'username' in data:
        user.login = data['username']

    if 'old_password' in data and check_password_hash(user.password,str(data['old_password'])):
        user.password = generate_password_hash(str(data['new_password']),method = 'pbkdf2:sha256')
        db.session.commit()
        return jsonify({"message":"Note updated"})
    return jsonify({"Message":"Invalid data"})


@app.route('/note',methods = ['POST'])
@token_required
def createNote(current_user):
    data = request.get_json()
    title = data['title']
    content = data['content']
    user_id = current_user.id
    if title:
        data = Note(title, content, user_id)
        db.session.add(data)
        db.session.commit()
        return jsonify({"Message":"Note added"})
    return jsonify({"Message":"Note not added"})

@app.route("/note",methods=['GET'])
@token_required
def getAllNotes(current_user):
    data = Note.query.filter_by(user_id = current_user.id)
    output = []

    for i in data:
        dict = {}
        dict['title'] = i.title
        dict['content'] = i.content
        output.append(dict)
    return jsonify({"Notes":output})

@app.route("/note/<note_id>",methods=['GET'])
@token_required
def getNote(current_user,note_id):
    data = Note.query.filter_by(id = note_id).first()
    if not data:
        return jsonify({'Message' : 'No note'})
    dict = {}
    dict['title'] = data.title
    dict['content'] = data.content
    return jsonify({"Note":dict})

@app.route("/note/<note_id>",methods=['DELETE'])
@token_required
def deleteNote(current_user,note_id):
    data = Note.query.filter_by(id = note_id).first()
    if not data:
        return jsonify({'Message' : 'No note'})
    Note.query.filter_by(id = note_id).delete()
    db.session.commit()
    return jsonify({"Message":"Note deleted"})

@app.route("/note/<note_id>",methods=['PUT'])
@token_required
def updateNote(current_user,note_id):
    data = request.get_json()
    note = Note.query.filter_by(id = note_id).first()
    if not note:
        return jsonify({'Message' : 'No note'})
    if 'title' in data:
        note.title = data['title']

    if 'content' in data:
        note.content = data['content']
    db.session.commit()
    return jsonify({'Message':"Note updated"})
