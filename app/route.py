from app import app
from app.note import notes_bp
from app.user import user_bp
from app.auth import log_bp


app.register_blueprint(notes_bp)
app.register_blueprint(user_bp)
app.register_blueprint(log_bp)
