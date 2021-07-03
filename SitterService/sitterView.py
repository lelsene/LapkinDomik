import io
import json
from datetime import date

from django.shortcuts import render
from django.http import HttpResponseRedirect

from SitterService import models


def sitters(request):
    token = request.COOKIES.get('token')
    user = models.User.objects.filter(token=token).first()

    if not user:
        return HttpResponseRedirect('/login')

    sorts = ['По умолчанию', 'По убыванию цены', 'По возрастанию цены']
    sexes = models.Sex.values
    cities = json.load(io.open('static/json/cities.json', encoding='utf-8'))
    types = list(models.PetType.objects.filter())

    profile = models.Profile.objects.filter(user=user).first()

    def reset():
        params = {'city': profile.city if profile.city else '', 'sex': [],
                  'petTypes': [], 'sort': sorts[0], 'priceFrom': 0,
                  'priceTo': max([profile.price for profile in models.Profile.objects.all()])}
        sitters = [
            (sitter, calculate_age(sitter.birthday), "; ".join([type.title for type in list(sitter.petTypes.all())]))
            for sitter in models.Profile.objects.filter(city=params['city'])
            if sitter.user.type == models.User.Type.SITTER]

        return params, sitters

    if request.method == 'GET':
        params, sitters = reset()

    elif request.method == 'POST':
        if 'reset' in request.POST:
            params, sitters = reset()

        if 'apply' in request.POST:
            params = {}
            params['city'] = request.POST.get('city')
            params['sort'] = request.POST.get('sort')

            params['priceFrom'] = request.POST.get('priceFrom')
            params['priceTo'] = request.POST.get('priceTo')

            params['priceFrom'] = int(params['priceFrom']) if params['priceFrom'].isdigit() else 0
            params['priceTo'] = int(params['priceTo']) \
                if params['priceTo'].isdigit() and int(params['priceTo']) >= params['priceFrom'] else \
                max([profile.price for profile in models.Profile.objects.all()])

            params['sex'] = request.POST.getlist('sex')
            params['sex'] = params['sex'] if len(params['sex']) > 0 else sexes
            params['petTypes'] = request.POST.getlist('petTypes')

            sitters = [
                (sit, calculate_age(sit.birthday), [type.title for type in list(sit.petTypes.all())])
                for sit in models.Profile.objects.filter(city=params['city'])
                if sit.user.type == models.User.Type.SITTER]

            sitters = [(sitter[0], sitter[1], "; ".join(sitter[2])) for sitter in sitters
                       if params['priceFrom'] <= sitter[0].price <= params['priceTo']
                       and sitter[0].sex in params['sex']
                       and sum([1 if type in params['petTypes'] else 0 for type in sitter[2]])
                       == len(params['petTypes'])]

            if params['sort'] == sorts[1]:
                sitters = sorted(sitters, key=lambda sitter: sitter[0].price, reverse=True)

            elif params['sort'] == sorts[2]:
                sitters = sorted(sitters, key=lambda sitter: sitter[0].price)

        if 'createApplication' in request.POST:
            id = request.POST.get('createApplication')
            return HttpResponseRedirect('/retreat_application/create/' + id)

    return render(request, 'sitters.html',
                  {'cities': cities, 'sitters': sitters, 'sexes': sexes, 'params': params,
                   'types': types, 'sorts': sorts})


def educations_view(request):
    token = request.COOKIES.get('token')
    user = models.User.objects.filter(token=token).first()

    if not user:
        return HttpResponseRedirect('/login')

    if request.POST:
        if 'test_view' in request.POST:
            id = request.POST.get('test_view')
            return HttpResponseRedirect('/sitter/test/' + id)
    educations = list(models.Education.objects.all())
    educations_test_id = [
        (education, models.Test.objects.filter(education=education).first().id) if models.Test.objects.filter(
            education=education).first() else (education, -1) for education in educations]
    return render(request, 'educations_view.html', {'educations': educations_test_id})


def education_view(request, education_id):
    token = request.COOKIES.get('token')
    user = models.User.objects.filter(token=token).first()

    if not user:
        return HttpResponseRedirect('/login')

    if request.POST:
        if 'test_view' in request.POST:
            id = request.POST.get('test_view')
            return HttpResponseRedirect('/sitter/test/' + id)

    education = models.Education.objects.filter(id=education_id).first()
    test_id = models.Test.objects.filter(education=education).first().id if models.Test.objects.filter(
        education=education).first() else -1
    return render(request, 'education_view.html', {'education': education, 'test_id': test_id})


def test_view(request, test_id):
    token = request.COOKIES.get('token')
    user = models.User.objects.filter(token=token).first()

    if not user:
        return HttpResponseRedirect('/login')

    test = models.Test.objects.filter(id=test_id).first()
    questions = list(models.Question.objects.filter(test=test))
    questions_answers = [(question, list(models.Answer.objects.filter(question=question))) for question in questions]

    if request.POST:
        if 'evaluation' in request.POST:
            answers = [(q, [(a, request.POST.get(f"q{q.id}a{a.id}")) for a in ans]) for q, ans in questions_answers]
            right = 0
            for question, answer in answers:
                count_answer = sum(
                    [1 if a.isRight and res == 'on' or not a.isRight and res is None else 0 for a, res in answer])
                right += 1 if count_answer == len(answer) else 0
            result = right / len(answers) * 100
            sitter_application = models.SitterApplication.objects.filter(
                user=user).first() if models.SitterApplication.objects.filter(
                user=user).first() else models.SitterApplication.objects.create(user=user, status='')

            sitter_education = models.SitterEducation.objects.filter(sitterApplication=sitter_application,
                                                                     education=test.education).first() \
                if models.SitterEducation.objects.filter(sitterApplication=sitter_application,
                                                         education=test.education).first() \
                else models.SitterEducation(education=test.education, sitterApplication=sitter_application)
            sitter_education.result = result
            sitter_education.save()
            return HttpResponseRedirect('/sitter/application')

    return render(request, 'test_view.html', {'questions_answers': questions_answers, 'test': test})


def sitter_applications(request):
    token = request.COOKIES.get('token')
    user = models.User.objects.filter(token=token).first()

    if not user:
        return HttpResponseRedirect('/login')

    sitter_applications = list(models.SitterApplication.objects.all())
    list_sitter_applications = []

    for sitter_application in sitter_applications:
        sitter_educations = models.SitterEducation.objects.filter(sitterApplication=sitter_application).all()
        sum = 0
        count = 0
        for sitter_education in sitter_educations:
            sum += sitter_education.result
            count += 1
        if count == 0:
            count += 1
        list_sitter_applications.append((sitter_application, sum / count))

    if request.method == 'POST':
        if 'sitterApplicationYes' in request.POST:
            sitterapplication = models.SitterApplication.objects.filter(
                id=int(request.POST.get('sitterApplicationYes'))).first()
            sitterapplication.status = "Принята"
            sitterapplication.save(update_fields=["status"])
            sitterapplication.user.type=models.User.Type.SITTER
            sitterapplication.user.save()

        if 'sitterApplicationNo' in request.POST:
            sitterapplication = models.SitterApplication.objects.filter(
                id=int(request.POST.get('sitterApplicationNo'))).first()
            sitterapplication.status = "Отклонена"
            sitterapplication.save(update_fields=["status"])

        return HttpResponseRedirect('/sitter/applications')

    return render(request, 'sitter_applications.html', {
        'sitter_applications': list_sitter_applications})


def sitter_application(request):
    token = request.COOKIES.get('token')
    user = models.User.objects.filter(token=token).first()

    if not user:
        return HttpResponseRedirect('/login')

    if user.type == models.User.Type.ADMIN:
        return HttpResponseRedirect('/')

    def ed_in_app(sitter_educations, education):
        for sitter_education in sitter_educations:
            if sitter_education.education == education:
                return sitter_education.result if sitter_education.result else 0
        return 0

    if request.POST:
        if 'createApplication' in request.POST:
            application = models.SitterApplication.objects.filter(user=user).first()
            application.status = models.Status.PROCESSING
            application.save()
            return HttpResponseRedirect('/sitter/application')

    educations = list(models.Education.objects.all())
    sitter_application = models.SitterApplication.objects.filter(user=user).first()
    sitter_educations = list(models.SitterEducation.objects.filter(sitterApplication=sitter_application))
    results = [ed_in_app(sitter_educations, education) for education in educations]
    totalResult = sum(results) / len(results) if len(results) != 0 else 0
    status = sitter_application.status if sitter_application else ""
    return render(request, 'sitter_application.html',
                  {'educations_results': zip(educations, results), 'totalResult': totalResult, 'status': status})


def calculate_age(birthday):
    today = date.today()
    age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
    mark = " лет" if (age > 9) and (age < 20) or (age > 110) or (age % 10 > 4) or (
            age % 10 == 0) else " год" if age % 10 == 0 else " года"
    return str(age) + mark
