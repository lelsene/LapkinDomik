from django.shortcuts import render
from django.http import HttpResponseRedirect
from datetime import datetime
from SitterService import models


def retreat_applications(request):
    token = request.COOKIES.get('token')
    user = models.User.objects.filter(token=token).first()

    if not user:
        return HttpResponseRedirect('/login')

    template = 'base.html'
    sexes = models.Sex.values
    if user.type == models.User.Type.SITTER:
        retreat_applications = list(models.RetreatApplication.objects.filter(sitter=user))
        applications = []
        for retreat_application in retreat_applications:
            applications.append((list(retreat_application.pets.all()), retreat_application, None))

        if request.method == 'POST':
            if 'retreatAccept' in request.POST:
                id = request.POST.get('retreatAccept')
                retreat_application = models.RetreatApplication.objects.filter(id=int(id)).first()
                retreat_application.status = models.Status.ACCEPTED
                retreat_application.save(update_fields=['status'])
                return HttpResponseRedirect('/retreat_applications')

            if 'retreatReject' in request.POST:
                id = request.POST.get('retreatReject')
                retreat_application = models.RetreatApplication.objects.filter(id=int(id)).first()
                retreat_application.status = models.Status.REJECTED
                retreat_application.save(update_fields=['status'])
                return HttpResponseRedirect('/retreat_applications')

        status = models.Status.PROCESSING
        return render(request, 'retreat_applications.html',
                      {'retreat_applications': applications, 'sexes': sexes, 'status': status, 'owner': False,
                       'admin': False, 'template': template})

    elif user.type == models.User.Type.OWNER:
        retreat_applications = list(models.RetreatApplication.objects.filter(owner=user))
        applications = []
        for retreat_application in retreat_applications:
            applications.append((list(retreat_application.pets.all()), retreat_application,
                                 models.Profile.objects.filter(user=retreat_application.sitter).first()))

        if request.method == 'POST':
            if 'retreatDelete' in request.POST:
                id = request.POST.get('retreatDelete')
                models.RetreatApplication.objects.filter(id=int(id)).delete()

                return HttpResponseRedirect('/retreat_applications')

        status = models.Status.PROCESSING
        return render(request, 'retreat_applications.html',
                      {'retreat_applications': applications, 'sexes': sexes, 'status': status, 'owner': True,
                       'admin': False, 'template': template})

    elif user.type == models.User.Type.ADMIN:
        template = 'base_admin.html'
        retreat_applications = list(models.RetreatApplication.objects.filter())
        applications = []
        for retreat_application in retreat_applications:
            applications.append((list(retreat_application.pets.all()), retreat_application,
                                 models.Profile.objects.filter(user=retreat_application.sitter).first()))

        status = models.Status.PROCESSING
        return render(request, 'retreat_applications.html',
                      {'retreat_applications': applications, 'sexes': sexes, 'status': status, 'owner': True,
                       'admin': True, 'template': template})


def retreat_application_create(request, sitter_id):
    token = request.COOKIES.get('token')
    user = models.User.objects.filter(token=token).first()

    if not user:
        return HttpResponseRedirect('/login')

    template = 'base.html'

    sitter = models.Profile.objects.filter(id=sitter_id).first()
    petTypes = list(sitter.petTypes.all())
    pets = [pet for pet in list(models.Pet.objects.filter(user=user)) if pet.petType in petTypes]
    application = models.RetreatApplication(sitter=sitter.user, owner=user, status='')
    daysCount = 0
    selectedPets = []
    message = ''

    if request.POST:
        if 'refresh' in request.POST or 'createApplication' in request.POST:
            selectedPets = [models.Pet.objects.filter(id=int(pet_id)).first() for pet_id in
                            request.POST.getlist('pets')]
            application.dateFrom = request.POST.get('dateFrom')
            application.dateTo = request.POST.get('dateTo')
            application.description = request.POST.get('description')
            daysCount = (datetime.strptime(application.dateTo, '%Y-%m-%d') -
                         datetime.strptime(application.dateFrom, '%Y-%m-%d')).days
            if daysCount < 1:
                message = "Выберите другие даты"
            else:
                application.totalCost = daysCount * sitter.price * len(selectedPets)

        if 'createApplication' in request.POST and message == '':
            application.status = models.Status.PROCESSING
            application.save()
            for pet in selectedPets:
                application.pets.add(pet)

            return HttpResponseRedirect('/retreat_applications')

    return render(request, 'retreat_application.html',
                  {'application': application, 'daysCount': daysCount, 'sitter': sitter, 'pets': pets,
                   'view': False, 'role': sitter, 'selectedPets': selectedPets, 'message': message, 'template':template})


def retreat_application_view(request, app_id):
    token = request.COOKIES.get('token')
    user = models.User.objects.filter(token=token).first()

    if not user:
        return HttpResponseRedirect('/login')

    template = 'base.html'
    if user.type == models.User.Type.ADMIN:
        template = 'base_admin.html'

    sexes = models.Sex.values
    petTypes = list(models.PetType.objects.all())

    application = models.RetreatApplication.objects.filter(id=app_id).first()
    sitter = models.Profile.objects.filter(user=application.sitter).first()
    pets = list(application.pets.all())

    daysCount = (application.dateTo - application.dateFrom).days
    application.dateFrom = application.dateFrom.strftime('%Y-%m-%d') if application.dateFrom else None
    application.dateTo = application.dateTo.strftime('%Y-%m-%d') if application.dateTo else None

    role = models.Profile.objects.filter(user=application.owner).first()
    if user.type == models.User.Type.OWNER:
        role = sitter

    return render(request, 'retreat_application.html',
                  {'application': application, 'daysCount': daysCount, 'sitter': sitter, 'pets': pets,
                   'sexes': sexes, 'petTypes': petTypes, 'view': True, 'role': role, 'template': template})
