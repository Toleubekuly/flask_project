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
