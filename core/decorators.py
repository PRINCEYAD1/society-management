from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """Restrict a view to users whose .role is in the given roles."""
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if request.user.role not in roles and not request.user.is_superuser:
                raise PermissionDenied("You do not have access to this page.")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
