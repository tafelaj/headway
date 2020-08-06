from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def user_is_lecturer(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_lecturer:
            return function(request, *args, **kwargs)
        else:
            if user.is_student:
                return redirect('headway:student_home')
            if user.is_admin:
                return redirect('administrator:dash')
    wrap.__doc__ = function.__doc__
    return wrap


def user_is_admin(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_admin:
            return function(request, *args, **kwargs)
        else:
            if user.is_student:
                return redirect('headway:student_home')
            if user.is_lecturer:
                return redirect('headway:lecturer_home')
    wrap.__doc__ = function.__doc__
    return wrap
