from app.models import User,Note
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from marshmallow import fields, validates, ValidationError

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True
    @validates('login')
    def validate_login(self, value):
        if not value:
            raise ValidationError("Login must not be empty.")
        if User.query.filter_by(login=value).first():
            raise ValidationError("Login must be unique.")

    @validates('password')
    def validate_password(self, value):
        if len(value) < 6:
            raise ValidationError("Password must be at least 6 characters long.")

    @validates('public_id')
    def validate_public_id(self, value):
        if User.query.filter_by(public_id=value).first():
            raise ValidationError("Public ID must be unique.")


class NoteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Note
        include_relationships = True
        exclude = ('user_id',)
    user_id = fields.Integer(dump_only=True, load_only=False)

