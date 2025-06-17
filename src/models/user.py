from . import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(512))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    borrows = db.relationship('Borrow', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            # Si aucun mot de passe n'est défini, on enregistre un hash pour bloquer l'accès futur
            self.set_password('changeme123!')
            db.session.commit()
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.name}>'
