from flask import Flask, render_template, request, jsonify, make_response
from app.config import db
from app.models import User, Note
from app.auth import token_required
from flask import Blueprint
from app.serializer import NoteSchema


notes_bp = Blueprint("notes_bp", __name__,url_prefix = "/note")


@notes_bp.route('', methods=['POST'])
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
        return jsonify({"Message": "Note added"})
    return jsonify({"Message": "Note not added"})


@notes_bp.route("", methods=['GET'])
@token_required
def getAllNotes(current_user):
    note_shema = NoteSchema(many = True)
    data = Note.query.filter_by(user_id=current_user.id)
    serialized_data = note_shema.dump(data)
    return jsonify({"Notes": serialized_data})


@notes_bp.route("/<note_id>", methods=['GET'])
@token_required
def getNote(current_user, note_id):
    note_shema = NoteSchema()
    data = Note.query.filter_by(id=note_id).first()
    if not data:
        return jsonify({'Message': 'No note'})
    serialized_data = note_shema.dump(data)
    return jsonify({"Note": serialized_data})


@notes_bp.route("/<note_id>", methods=['DELETE'])
@token_required
def deleteNote(current_user, note_id):
    data = Note.query.filter_by(id=note_id).first()
    if not data:
        return jsonify({'Message': 'No note'})
    Note.query.filter_by(id=note_id).delete()
    db.session.commit()
    return jsonify({"Message": "Note deleted"})


@notes_bp.route("/<note_id>", methods=['PUT'])
@token_required
def updateNote(current_user, note_id):
    data = request.get_json()
    note = Note.query.filter_by(id=note_id).first()
    if not note:
        return jsonify({'Message': 'No note'})
    if 'title' in data:
        note.title = data['title']

    if 'content' in data:
        note.content = data['content']
    db.session.commit()
    return jsonify({'Message': "Note updated"})
