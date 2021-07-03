import io
import json
import re

from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponseRedirect

from SitterService import models


def profile(request):
    token = request.COOKIES.get('token')
    user = models.User.objects.filter(token=token).first()

    if not user:
        return HttpResponseRedirect('/login')

    template = 'base.html'
    if user.type == models.User.Type.ADMIN:
        template = 'base_admin.html'

    sexes = models.Sex.values
    petTypes = list(models.PetType.objects.all())
    cities = json.load(io.open('static/json/cities.json', encoding='utf-8'))
    profile = models.Profile.objects.filter(user=user).first()

    if user.type == models.User.Type.OWNER:
        pets = list(models.Pet.objects.filter(user=user))

        if not profile:
            profile = models.Profile()

        if request.method == 'POST':
            if 'profileSave' in request.POST:
                profile.user = user
                profile.name = request.POST.get('name')
                profile.surname = request.POST.get('surname')

                image = request.FILES.get('image') if request.FILES else None
                image_path = handle_uploaded_file(image, profile)
                if image_path:
                    profile.image = image_path

                profile.sex = request.POST.get('sex')
                profile.birthday = request.POST.get('birthday')
                profile.city = request.POST.get('city')
                profile.phoneNumber = request.POST.get('phone')

                profile.save()

                return HttpResponseRedirect('/profile')

            elif 'petSave' in request.POST:
                id = request.POST.get('petSave')

                if id.isdigit():
                    pet = models.Pet.objects.filter(id=int(id)).first()
                else:
                    pet = models.Pet()
                    pet.user = user

                pet.name = request.POST.get(f'petName_{id}') if request.POST.get(f'petName_{id}') else ''
                pet.age = int(request.POST.get(f'petAge_{id}')) if request.POST.get(f'petAge_{id}') else 0
                pet.sex = request.POST.get(f'petSex_{id}') if request.POST.get(f'petSex_{id}') else ''
                pet.petType = models.PetType.objects.filter(title=request.POST.get(f'petType_{id}')).first() \
                    if request.POST.get(f'petType_{id}') else models.PetType.objects.filter().first()
                pet.description = request.POST.get(f'petDescription_{id}') \
                    if request.POST.get(f'petDescription_{id}') else ''

                image = request.FILES.get(f'petImage_{id}') if request.FILES else None
                image_path = handle_uploaded_file(image, pet)
                if image_path:
                    pet.image = image_path

                if pet.name != '' and pet.sex != '':
                    pet.save()

                return HttpResponseRedirect('/profile')

            elif 'petDelete' in request.POST:
                models.Pet.objects.filter(id=int(request.POST.get('petDelete'))).delete()

                return HttpResponseRedirect('/profile')

            elif 'petAdd' in request.POST:
                pets.append(models.Pet(name="", description=""))

        if profile.birthday:
            profile.birthday = profile.birthday.strftime('%Y-%m-%d')

        return render(request, 'owner_profile.html',
                      {'profile': profile, 'cities': cities, 'pets': pets, 'sexes': sexes, 'petTypes': petTypes, 'template':template})

    elif user.type == models.User.Type.SITTER:
        if not profile:
            profile = models.Profile()
            profile_petTypes = []
        else:
            profile.birthday = profile.birthday.strftime('%Y-%m-%d') if profile.birthday else None
            profile_petTypes = [petType.title for petType in list(profile.petTypes.all())]

        if request.method == 'POST':
            if 'profileSave' in request.POST:
                profile.user = user
                profile.name = request.POST.get('name')
                profile.surname = request.POST.get('surname')

                image = request.FILES.get('image') if request.FILES else None
                image_path = handle_uploaded_file(image, profile)
                if image_path:
                    profile.image = image_path

                profile.sex = request.POST.get('sex')
                profile.birthday = request.POST.get('birthday')
                profile.city = request.POST.get('city')
                profile.phoneNumber = request.POST.get('phone')
                profile.description = request.POST.get('description')
                profile.price = float(request.POST.get('price'))

                profile.save()

                petTypes = request.POST.getlist('petType')
                for type in petTypes:
                    profile.petTypes.add(models.PetType.objects.filter(title=type).first())

                return HttpResponseRedirect('/profile')

        return render(request, 'sitter_profile.html',
                      {'profile': profile, 'cities': cities, 'sexes': sexes, 'petTypes': petTypes,
                       'profile_petTypes': profile_petTypes, 'template':template})

    elif user.type == models.User.Type.ADMIN:
        dict = {'email': user.email, 'password_old': '', 'password_new': '', 'emailMessage': '',
                'passwordMessage_old': '', 'passwordMessage_new': ''}

        if request.method == 'POST':
            if 'profileSave' in request.POST:
                dict['email'] = request.POST.get('Email')
                dict['password_old'] = request.POST.get('Password_old')
                dict['password_new'] = request.POST.get('Password_new')
                regex = r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$"

                if dict['email'] == user.email:
                    dict['emailMessage'] = ''

                elif re.search(regex, dict['email']) is None:
                    dict['emailMessage'] = 'Электронная почта введена неверно или уже занята'

                elif len(models.User.objects.filter(email=dict['email'])) != 0:
                    dict['emailMessage'] = 'Электронная почта введена неверно или уже занята'

                else:
                    user.email = dict['email']
                    user.save(update_fields=["email"])
                    dict['emailMessage'] = 'Электронная почта обновлена'

                if dict['password_old'] != '':
                    if check_password(dict['password_old'], user.password) is False:
                        dict['passwordMessage_old'] = 'Некорректный пароль'

                    elif len(dict['password_new']) < 3:
                        dict['passwordMessage_new'] = 'Пароль выбран неверно'

                    elif dict['password_old'] == dict['password_new']:
                        dict['passwordMessage_new'] = 'Пароль совпадает со старым'

                    else:
                        user.password = make_password(dict['password_new'])
                        user.save(update_fields=["password"])
                        dict['password_old'] = ''
                        dict['password_new'] = ''
                        dict['passwordMessage_new'] = 'Пароль обновлен'

        return render(request, 'admin_profile.html', dict)


def user_profile(request, user_id):
    token = request.COOKIES.get('token')
    user = models.User.objects.filter(token=token).first()

    if not user:
        return HttpResponseRedirect('/login')

    template = 'base.html'
    if user.type == models.User.Type.ADMIN:
        template = 'base_admin.html'

    sexes = models.Sex.values
    petTypes = list(models.PetType.objects.all())
    cities = json.load(io.open('static/json/cities.json', encoding='utf-8'))

    profile_user = models.User.objects.filter(id=user_id).first()
    profile = models.Profile.objects.filter(user=profile_user).first()

    if profile_user.type == models.User.Type.OWNER:
        pets = list(models.Pet.objects.filter(user=profile_user))

        if not profile:
            profile = models.Profile()

        if profile.birthday:
            profile.birthday = profile.birthday.strftime('%Y-%m-%d')

        return render(request, 'owner_profile.html',
                      {'profile': profile, 'cities': cities, 'pets': pets, 'sexes': sexes, 'petTypes': petTypes,
                       'view': True, 'template': template})

    elif profile_user.type == models.User.Type.SITTER:
        if not profile:
            profile = models.Profile()
            profile_petTypes = []
        else:
            profile.birthday = profile.birthday.strftime('%Y-%m-%d') if profile.birthday else None
            profile_petTypes = [petType.title for petType in list(profile.petTypes.all())]

        return render(request, 'sitter_profile.html',
                      {'profile': profile, 'cities': cities, 'sexes': sexes, 'petTypes': petTypes,
                       'profile_petTypes': profile_petTypes, 'view': True, 'template': template})

    return HttpResponseRedirect('/')


def handle_uploaded_file(file, instance):
    try:
        if not file:
            return None
        path = models.user_directory_path(instance, file.name)
        with open(path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return path[7:]
    except Exception as e:
        print(e)
        return None


def main(request):
    token = request.COOKIES.get('token')
    user = models.User.objects.filter(token=token).first()

    template = 'base.html'
    if user and user.type == models.User.Type.ADMIN:
        template = 'base_admin.html'

    if request.POST:
        if 'registr' in request.POST:
            return HttpResponseRedirect('/registration')
        if 'auth' in request.POST:
            return HttpResponseRedirect('/login')
    return render(request, 'main.html', {'template': template})
