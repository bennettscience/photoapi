from dataclasses import dataclass
from app import db


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(64), index=True, unique=True)
#     email = db.Column(db.String(120), index=True, unique=True)
#     pass_hash = db.Column(db.String(128))


@dataclass
class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128), index=True)
    upload_date = db.Column(db.Integer)
    public = db.Column(db.Boolean, default=False)

    def __init__(self, title, upload_date, public):
        self.title = title
        self.upload_date = upload_date
        self.public = public

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
