# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from .forms import LoginForm, SignUpForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group
from apps.home.models import UsersMapping
from datetime import datetime, timedelta, timezone



def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Невірно введений логін або пароль'
        else:
            msg = 'Не вдалося прийняти форму'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created successfully.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


@csrf_exempt
def create_user(request):
    request_data_GET = dict(request.GET)
    request_data_POST = dict(request.POST)
    if request.META["REMOTE_ADDR"] != "127.0.0.1":
        return JsonResponse(
            {"status": "False", "details": "Request received from not authorized IP"})
    first_name = request_data_GET.get("first_name")[0]
    last_name = request_data_GET.get("last_name")[0]
    role = request_data_GET.get("role")[0]
    territorial_manager = request_data_GET.get("territorial_manager")
    if territorial_manager:
        territorial_manager = territorial_manager[0]
    if role == "territorial_manager_km" and not territorial_manager:
        return JsonResponse(
            {"status": "False", "details": "Client manager must be followed by territorial_manager"})

    username = f"{first_name}_{last_name}"
    raw_password = "abcdefgh"
    user_obj = User.objects.filter(username=f"{first_name}_{last_name}").first()
    if user_obj:
        return JsonResponse(
            {"status": "False", "details": "User already exists."})
    user = User.objects.create_user(username=username, password=raw_password)
    if user:
        user.first_name = first_name
        user.last_name = last_name
        group = Group.objects.get(name=role)
        group.user_set.add(user)
        user_mapping = UsersMapping(user=user, password=raw_password)
        if role == "territorial_manager_km":
            tm_first_name = territorial_manager.split()[0]
            tm_last_name = territorial_manager.split()[1]
            tm_user = User.objects.filter(first_name=tm_first_name, last_name=tm_last_name).first()

            if tm_user:
                user_mapping.related_to = tm_user
        user_mapping.save()
        group.save()
        user.save()
        return JsonResponse({"status": "True", "request_data_GET": request_data_GET, "request_data_POST": request_data_POST})
    else:
        return JsonResponse(
            {"status": "False", "details": "Unable to create user"})


@csrf_exempt
def deactivate_user(request):
    if request.META["REMOTE_ADDR"] != "127.0.0.1":
        return JsonResponse(
            {"status": "False", "details": "Request received from not authorized IP"})
    request_data_GET = dict(request.GET)
    request_data_POST = dict(request.POST)
    first_name = request_data_GET.get("first_name")[0]
    last_name = request_data_GET.get("last_name")[0]
    user_obj = User.objects.filter(username=f"{first_name}_{last_name}").first()
    if user_obj:
        user_obj.is_active = False
        user_obj.save()
        return JsonResponse(
            {"status": "True", "request_data_GET": request_data_GET, "request_data_POST": request_data_POST})
    else:
        return JsonResponse(
            {"status": "False", "details": "User not found"})


@csrf_exempt
def auth_user(request):
    request_data_GET = dict(request.GET)
    request_data_POST = dict(request.POST)
    first_name = request_data_GET.get("first_name")[0]
    last_name = request_data_GET.get("last_name")[0]
    token = request_data_GET.get("token")[0]

    user_obj = User.objects.filter(username=f"{first_name}_{last_name}").first()
    if not user_obj.is_active:
        return JsonResponse(
                    {"status": "False", "details": "User is out of activity."})
    if user_obj:
        username = user_obj.username
        mapping = UsersMapping.objects.filter(user_id=user_obj.id).first()
        user = None
        if token != mapping.auth_token:
            if request.META["REMOTE_ADDR"] != "127.0.0.1":
                return JsonResponse(
                    {"status": "False", "details": "Request received from not authorized IP"})
            mapping.auth_token = token
            timestamp = datetime.now(timezone.utc)
            mapping.login_timestamp = timestamp
            mapping.save()
            return JsonResponse(
                {"status": "True", "request_data_GET": request_data_GET, "request_data_POST": request_data_POST})
        else:
            time_now = datetime.now(timezone.utc)
            if time_now - mapping.login_timestamp < timedelta(minutes=1):
                password = mapping.password
                user = authenticate(username=username, password=password)
            else:
                return JsonResponse(
                    {"status": "False", "details": "Out of authorisation time"})

        if user is not None:
            login(request, user)
            return redirect("/")
    return JsonResponse({"status": "True", "request_data_GET": request_data_GET, "request_data_POST": request_data_POST})


@csrf_exempt
def update_user(request):
    if request.META["REMOTE_ADDR"] != "127.0.0.1":
        return JsonResponse(
            {"status": "False", "details": "Request received from not authorized IP"})
    request_data_GET = dict(request.GET)
    request_data_POST = dict(request.POST)
    first_name = request_data_GET.get("first_name")[0]
    last_name = request_data_GET.get("last_name")[0]
    first_name_new = request_data_GET.get("first_name_new")[0]
    last_name_new = request_data_GET.get("last_name_new")[0]
    role_new = request_data_GET.get("role_new")[0]

    user_obj = User.objects.filter(username=f"{first_name}_{last_name}").first()

    if user_obj:
        mapping = UsersMapping.objects.filter(user=user_obj).first()
        user_obj.first_name = first_name_new
        user_obj.last_name = last_name_new
        user_obj.username = f"{first_name_new} {last_name_new}"
        group = Group.objects.get(name=role_new)
        group.user_set.add(user_obj)
        if role_new == "territorial_manager_km":
            try:
                territorial_new = request_data_GET.get("territorial_manager_new")[0]
            except:
                return JsonResponse(
                    {"status": "False", "details": "Territorial manager not specified for client manager"})
            tm_first_name = territorial_new.split()[0]
            tm_last_name = territorial_new.split()[1]
            tm_user = User.objects.get(first_name=tm_first_name, last_name=tm_last_name)
            if tm_user:
                mapping.related_to = tm_user
            else:
                return JsonResponse(
                    {"status": "False", "details": f"TM user {territorial_new} not found."})
        mapping.save()
        group.save()
        user_obj.save()
        return JsonResponse(
            {"status": "True", "request_data_GET": request_data_GET, "request_data_POST": request_data_POST})
    else:
        return JsonResponse(
            {"status": "False", "details": "User not found"})