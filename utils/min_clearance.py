from functools import wraps
from flask import abort, redirect, url_for, request
from flask_login.utils import current_user

from main.modules.accounts.ClearanceEnum import ClearanceEnum


def min_clearance(permission: ClearanceEnum = ClearanceEnum.NORMAL):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('accounts.login', next=request.url))
            if not current_user.clearance >= permission:
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator
