"""Candidate utilities"""
from functools import wraps
from flask import abort, redirect, url_for
from flask_login import current_user


def candidate_required(f):
    """Decorator to require candidate role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role != 'candidate':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
