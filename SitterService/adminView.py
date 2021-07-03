from django.shortcuts import render
from django.http import HttpResponseRedirect

from SitterService import models


def users(request):
    token = request.COOKIES.get('token')
    user = models.User.objects.filter(token=token).first()

    if not user or user.type != models.User.Type.ADMIN:
        return HttpResponseRedirect('/login')

    sexes = models.Sex.values
    types = [('Sitter', 'Ситтер'), ('Owner', 'Хозяин')]
    users = list(models.User.objects.all())
    list_users = [(user, models.Profile.objects.filter(user=user).first())
                  for user in users
                  if user.type != models.User.Type.ADMIN]

    if request.method == 'POST':
        if 'userDelete' in request.POST:
            models.User.objects.filter(id=int(request.POST.get('userDelete'))).delete()

        return HttpResponseRedirect('/users')

    return render(request, 'users.html', {
        'list_users': list_users, 'sexes': sexes, 'types': types})
