from main import db
from flask_login import UserMixin

from main.modules.accounts.ClearanceEnum import ClearanceEnum


class Account(db.Model, UserMixin):
    def get_id(self):
        return self.account_id

    account_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    clearance = db.Column(db.Integer, default=ClearanceEnum.UNVERIFIED, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
