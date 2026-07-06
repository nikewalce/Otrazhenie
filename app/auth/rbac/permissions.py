from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def permission_required(permission_name: str):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_permission(permission_name):
                abort(403)
            return view_func(*args, **kwargs)
        return wrapped_view
    return decorator
