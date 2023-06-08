def user_group(request):
    user_group = None
    if request.user.is_authenticated:
        user_group = request.user.groups.first()
    return str(user_group)