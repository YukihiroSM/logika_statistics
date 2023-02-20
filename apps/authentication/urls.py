# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from .views import login_view, register_user, create_user, auth_user, deactivate_user, update_user
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("create_user", create_user, name="create_user"),
    path("deactivate_user", deactivate_user, name="deactivate_user"),
    path("auth_user", auth_user, name="auth_user"),
    path("update_user", update_user, name="update_user")
]
