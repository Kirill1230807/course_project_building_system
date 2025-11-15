from accounts.models import CustomUser

def user_context(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return {}

    try:
        user = CustomUser.objects.get(id=user_id)
        return {
            "current_user": user,
            "current_role": user.role,
        }
    except CustomUser.DoesNotExist:
        return {}