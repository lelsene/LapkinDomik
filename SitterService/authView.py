import os
import re
import binascii

from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponseRedirect

from SitterService import models


def registration(request):
    dict = {"email": '', "password": '', "emailMessage": '', "passwordMessage": ''}
    if request.method == 'POST':
        validation = True
        dict['email'] = request.POST.get('Email') if request.POST.get('Email') else ''
        dict['password'] = request.POST.get('Password') if request.POST.get('Password') else ''
        regex = r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$"

        if re.search(regex, dict['email']) is None:
            dict['emailMessage'] = 'Электронная почта введена неверно или уже занята'
            validation = False

        if len(models.User.objects.filter(email=dict['email'])) != 0:
            dict['emailMessage'] = 'Электронная почта введена неверно или уже занята'
            validation = False

        if len(dict['password']) < 3:
            dict['passwordMessage'] = 'Пароль выбран неверно'
            validation = False

        if validation:
            user = models.User(email=dict['email'], password=make_password(dict['password']),
                               token=binascii.hexlify(os.urandom(127)).decode())
            user.save()
            response = HttpResponseRedirect('/profile')
            response.set_cookie('token', user.token)
            return response
        else:
            return render(request, 'registration.html', dict)
    else:
        return render(request, 'registration.html', dict)


def login(request):
    dict = {"email": '', "password": '', "emailMessage": '', "passwordMessage": ''}
    if request.method == 'POST':
        auth = True
        dict['email'] = request.POST.get('Email') if request.POST.get('Email') else ''
        dict['password'] = request.POST.get('Password') if request.POST.get('Password') else ''

        user = models.User.objects.filter(email=dict['email']).first()

        if user is None:
            dict['emailMessage'] = 'Электронная почта введена неверно или не существует'
            auth = False
        else:
            if check_password(dict['password'], user.password) is False:
                dict['passwordMessage'] = 'Некорректный пароль'
                auth = False

        if auth:
            user.token = binascii.hexlify(os.urandom(127)).decode()
            user.save(update_fields=["token"])
            response = HttpResponseRedirect('/profile')
            response.set_cookie('token', user.token)
            return response
        else:
            return render(request, 'login.html', dict)
    return render(request, 'login.html', dict)


def logout(request):
    token = request.COOKIES.get('token')
    user = models.User.objects.filter(token=token).first()

    if not user:
        return HttpResponseRedirect('/login')

    user.token = ''
    user.save(update_fields=['token'])
    response = HttpResponseRedirect('/')
    response.delete_cookie('token')
    return response
