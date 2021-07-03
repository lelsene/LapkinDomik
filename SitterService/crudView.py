from django.shortcuts import render
from django.http import HttpResponseRedirect
from SitterService import models


def educations(request):
    token = request.COOKIES.get('token')
    user = models.User.objects.filter(token=token).first()

    if not user or user.type != models.User.Type.ADMIN:
        return HttpResponseRedirect('/login')

    educations = list(models.Education.objects.all())

    if request.method == 'POST':

        if 'educationAdd' in request.POST:
            educations = [models.Education(title='', source='').save()] + educations

        if 'educationDelete' in request.POST:
            models.Education.objects.filter(id=int(request.POST.get('educationDelete'))).delete()

        if 'educationUpdate' in request.POST:
            education = models.Education.objects.filter(id=int(request.POST.get('educationUpdate'))).first()
            dict = {'title': education.title, 'source': education.source, 'description': education.description}

            dict['title'] = request.POST.get(f'Title_{request.POST.get("educationUpdate")}')
            dict['source'] = request.POST.get(f'Source_{request.POST.get("educationUpdate")}')
            dict['description'] = request.POST.get(f'Description_{request.POST.get("educationUpdate")}')

            education.title = dict['title']
            education.source = dict['source']
            education.description = dict['description']
            education.save()

        return HttpResponseRedirect('/educations')

    return render(request, 'educations.html', {
        'educations': educations})


def tests(request):
    token = request.COOKIES.get('token')
    user = models.User.objects.filter(token=token).first()

    if not user or user.type != models.User.Type.ADMIN:
        return HttpResponseRedirect('/login')

    tests = list(models.Test.objects.all())
    list_tests = [(test, models.Question.objects.filter(test=test).all())
                  for test in tests]

    educations = list(models.Education.objects.all())

    Message = ''
    if request.method == 'POST':

        if 'testAdd' in request.POST:
            if len(models.Education.objects.all()) != 0:
                tests = models.Test.objects.all()
                found = False
                for education in educations:
                    flag = 0
                    for test in tests:
                        if education.title != test.education.title:
                            flag += 1
                    if flag == len(tests):
                        test = models.Test.objects.create(title='', education=education)
                        found = True
                        break
                if not found:
                    Message = 'Нет доступных тем обучения'
            else:
                Message = 'Нет доступных тем обучения'

        if 'testDelete' in request.POST:
            models.Test.objects.filter(id=int(request.POST.get('testDelete'))).delete()

        if 'testUpdate' in request.POST:
            test = models.Test.objects.filter(id=int(request.POST.get('testUpdate'))).first()
            dict = {'title': test.title, 'education': test.education}

            dict['title'] = request.POST.get(f'Title_{request.POST.get("testUpdate")}')
            dict['education'] = request.POST.get(f'Education_{request.POST.get("testUpdate")}')

            test.title = dict['title']
            test.education = models.Education.objects.filter(title=dict['education']).first()
            test.save()

    tests = list(models.Test.objects.all())
    list_tests = [(test, models.Question.objects.filter(test=test).all())
                  for test in tests]
    educations = list(models.Education.objects.all())

    free_educations = []
    for education in educations:
        flag = 0
        for test in tests:
            if education.title != test.education.title:
                flag += 1
        if flag == len(tests):
            free_educations.append((education))

    return render(request, 'tests.html', {
        'list_tests': list_tests, 'educations': educations, 'free_educations': free_educations, 'Message': Message})


def questions(request):
    token = request.COOKIES.get('token')
    user = models.User.objects.filter(token=token).first()

    if not user or user.type != models.User.Type.ADMIN:
        return HttpResponseRedirect('/login')

    questions = list(models.Question.objects.all())
    list_questions = [(question, models.Answer.objects.filter(question=question).all())
                      for question in questions]

    Message = ''
    if request.method == 'POST':

        if 'questionAdd' in request.POST:
            if len(models.Test.objects.all()) != 0:
                question = models.Question.objects.create(title='', test=models.Test.objects.filter().first())
                list_questions = list_questions + [
                    (question, list(models.Answer.objects.filter(question=question).all()))]
            else:
                Message = 'Нет доступных тестов'

        if 'questionDelete' in request.POST:
            models.Question.objects.filter(id=int(request.POST.get('questionDelete'))).delete()

        if 'questionUpdate' in request.POST:
            question = models.Question.objects.filter(id=int(request.POST.get('questionUpdate'))).first()
            dict = {'title': question.title, 'test': question.test}

            dict['title'] = request.POST.get(f'Title_{request.POST.get("questionUpdate")}')
            dict['test'] = request.POST.get(f'Test_{request.POST.get("questionUpdate")}')

            question.title = dict['title']
            question.test = models.Test.objects.filter(title=dict['test']).first()
            question.save()

    tests = list(models.Test.objects.all())
    questions = list(models.Question.objects.all())
    list_questions = [(question, models.Answer.objects.filter(question=question).all())
                      for question in questions]

    return render(request, 'questions.html', {
        'list_questions': list_questions, 'tests': tests, 'Message': Message})


def answers(request):
    token = request.COOKIES.get('token')
    user = models.User.objects.filter(token=token).first()

    if not user or user.type != models.User.Type.ADMIN:
        return HttpResponseRedirect('/login')

    answers = list(models.Answer.objects.all())

    Message = ''
    if request.method == 'POST':

        if 'answerAdd' in request.POST:
            if len(models.Question.objects.all()) != 0:
                answer = models.Answer.objects.create(title='', isRight=False,
                                                      question=models.Question.objects.first())
            else:
                Message = 'Нет доступных вопросов'

        if 'answerDelete' in request.POST:
            models.Answer.objects.filter(id=int(request.POST.get('answerDelete'))).delete()

        if 'answerUpdate' in request.POST:
            answer = models.Answer.objects.filter(id=int(request.POST.get('answerUpdate'))).first()
            dict = {'title': answer.title, 'isRight': answer.isRight, 'question': answer.question}

            dict['title'] = request.POST.get(f'Title_{request.POST.get("answerUpdate")}')
            dict['isRight'] = request.POST.get(f'IsRight_{request.POST.get("answerUpdate")}')
            dict['question'] = request.POST.get(f'Question_{request.POST.get("answerUpdate")}')

            answer.title = dict['title']
            answer.isRight = True if dict['isRight'] else False
            answer.question = models.Question.objects.filter(title=dict['question']).first()
            answer.save()

    answers = list(models.Answer.objects.all())
    questions = list(models.Question.objects.all())

    return render(request, 'answers.html', {
        'answers': answers, 'questions': questions, 'Message': Message})
