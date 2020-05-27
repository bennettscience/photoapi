from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128), index=True)
    upload_date = db.Column(db.Integer)
    public = db.Column(db.Boolean, default=False)
    filename = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, upload_date, public, filename):
        self.title = title
        self.upload_date = upload_date
        self.public = public
        self.filename = filename

    def __repr__(self):
        return f"Photo: {self.title}"

    def get_id(self):
        return self.id

    def set_public(self):
        self.public = not self.public
        db.session.commit()

    def set_title(self, title):
        self.title = title
        db.session.commit()

    def update(self, k, v):
        setattr(self, k, v)
        db.session.commit()
        return self


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    display_name = db.Column(db.String(64))
    pass_hash = db.Column(db.String(128))
    photos = db.relationship('Photo', backref='photographer', lazy='dynamic')

    def __repr__(self):
        return f'User: {self.name}'

    def set_password(self, password):
        self.pass_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pass_hash, password)
