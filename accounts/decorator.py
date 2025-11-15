from django.shortcuts import redirect

def require_role(roles: list):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            role = request.session.get("role")
            if role not in roles:
                return redirect("no_access")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator