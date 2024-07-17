from flask import Flask, jsonify, request, Blueprint
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import  ValidationError

from app.config import db
from app.serializer import UserSchema
from app.auth import token_required
from app.models import User, Note

user_bp = Blueprint('user_bp', __name__, url_prefix="/user")




@user_bp.route('', methods=['GET'])
@token_required
def get_all_users(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})
    user_schema = UserSchema(many=True)
    users = User.query.all()
    serialized_users = user_schema.dump(users)
    return jsonify({"users": serialized_users})


@user_bp.route('/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})
    user_schema = UserSchema()
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'No user found'})
    serialized_user = user_schema.dump(user)
    return jsonify({'user': serialized_user})


@user_bp.route('/<public_id>', methods=['POST'])
@token_required
def promote_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'No user found'})
    user.admin = True
    db.session.commit()
    return jsonify({'message': 'User has been promoted'})


@user_bp.route('/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'No user found'})
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User has been deleted"})


@user_bp.route('/<public_id>', methods=['PUT'])
@token_required
def update_user(current_user, public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'No user found'})
    data = request.get_json()
    if 'username' in data:
        user.login = data['username']
    if 'old_password' in data and check_password_hash(user.password, str(data['old_password'])):
        user.password = generate_password_hash(
            str(data['new_password']), method='pbkdf2:sha256')
    db.session.commit()
    return jsonify({'message': 'User updated'})

