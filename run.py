from app import app

import sys
import os
from app.config import db
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создание всех таблиц в базе данных
    app.run(debug=True)
