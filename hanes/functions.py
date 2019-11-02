
from django.shortcuts import redirect


def redirect_if_logged(redirect_url=None):
    """
    Decorator for views that checks that the user is already logged in, redirecting
    to certain URL if so.
    """
    def _decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_active():
                return redirect(redirect_url, *args, **kwargs)
            else:
                return view_func(request, *args, **kwargs)
        return _wrapped_view
