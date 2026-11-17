
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect


def role_required(role):

    def decorator(view_func):

        @login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if request.user.role != role:

                messages.error(
                    request,
                    'You are not authorized to access this page.'
                )

                return redirect('login')

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
