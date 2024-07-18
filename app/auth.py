import jwt
import uuid
import datetime

from flask import Flask, request, jsonify, make_response, Blueprint, url_for
from flask_mail import Mail, Message

from functools import wraps
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash

from app import app
from app.models import User
from app.config import db

log_bp = Blueprint('log_bp', __name__, url_prefix='/')
mail = Mail(app)
s = URLSafeTimedSerializer('SecretKey')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@log_bp.route('', methods=['GET'])
@log_bp.route('/login', methods=['GET'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(login=auth.username).first()

    if not user:
        return make_response("Could not find this login", 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response("Invalid password", 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


@log_bp.route('/register', methods=['POST'])
def create_user():
    data = request.get_json()
    email = data['login']
    hashed_password = generate_password_hash(str(data['password']), method='pbkdf2:sha256')

    token = s.dumps({'email': email, 'password': hashed_password}, salt='email_confirm')
    msg = Message('Confirm email', sender='Ertoshka04@gmail.com', recipients=[email])
    link = url_for('log_bp.confirm_email', token=token, _external=True)
    msg.body = f"Your confirm link {link}"
    mail.send(msg)
    return jsonify({'Message': 'Confirm link sent to your email'})


@log_bp.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        data = s.loads(token, salt='email_confirm', max_age=3600)
        user = User(public_id=str(uuid.uuid4()), login=data['email'], password=data['password'], admin=False)
        db.session.add(user)
        db.session.commit()
    except SignatureExpired:
        return jsonify({"Message": "Token expired!"})

    return jsonify({"Message": "New user created!"})
