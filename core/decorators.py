from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def role_required(*roles):
    """Equivalent of the Flask @role_required(*roles) decorator."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated or request.user.role not in roles:
                messages.error(request, "Access denied.")
                return redirect("core:index")
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator
