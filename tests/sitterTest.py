from django.test import TestCase
from django.urls import reverse
from SitterService import models
from django.contrib.auth.hashers import make_password


class SitterTest(TestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.applications_url = reverse('sitter_applications')
        self.profile_url = reverse('profile')

        self.user = models.User.objects.create(
            email="test@test.ru",
            password=make_password("test"),
            type=models.User.Type.ADMIN
        )

        response_login = self.client.post(self.login_url, {
            "Email": "test@test.ru",
            "Password": "test"
        })

        self.assertEqual(response_login.url, self.profile_url)

        self.sitter = models.User.objects.create(email="q@q.ru", password=make_password("test"))

        self.application = models.SitterApplication.objects.create(user=self.sitter)

    def test_approve_sitter_positive(self):
        response = self.client.post(self.applications_url, {
            'sitterApplicationYes': self.application.id
        })

        sitter = models.User.objects.filter(id=self.sitter.id).first()
        application = models.SitterApplication.objects.filter(id=self.application.id).first()

        self.assertEqual(response.url, self.applications_url)
        self.assertEqual(application.status, models.Status.ACCEPTED)
        self.assertEqual(sitter.type, models.User.Type.SITTER)

    def test_reject_sitter_positive(self):
        response = self.client.post(self.applications_url, {
            'sitterApplicationNo': self.application.id
        })

        sitter = models.User.objects.filter(id=self.sitter.id).first()
        application = models.SitterApplication.objects.filter(id=self.application.id).first()

        self.assertEqual(response.url, self.applications_url)
        self.assertEqual(application.status, models.Status.REJECTED)
        self.assertEqual(sitter.type, models.User.Type.OWNER)

    def test_view_educations_positive(self):
        response = self.client.get(reverse('educations_view'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(reverse('educations_view'), getattr(response, 'request')['PATH_INFO'])

    def test_view_education_positive(self):
        education = models.Education.objects.create(
            title='TestEducation',
            source='TestSource',
            description='TestDescription'
        )

        response = self.client.get(reverse('education_view', args=[education.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(reverse('education_view', args=[education.id]), getattr(response, 'request')['PATH_INFO'])

    def test_view_test_positive(self):
        education = models.Education.objects.create(
            title='TestEducation',
            source='TestSource',
            description='TestDescription'
        )

        test = models.Test.objects.create(
            title='Test',
            education=education
        )

        response = self.client.post(reverse('educations_view'), {
            'test_view': test.id
        })

        self.assertEqual(response.url, reverse('test_view', args=[test.id]))

    def test_evaluation_test_positive(self):
        education = models.Education.objects.create(
            title='TestEducation',
            source='TestSource',
            description='TestDescription'
        )

        test = models.Test.objects.create(
            title='Test',
            education=education
        )

        question = models.Question.objects.create(
            title="TestQuestion",
            test=test
        )

        answer = models.Answer.objects.create(
            title='TestAnswer',
            isRight=True,
            question=question
        )

        response_login = self.client.post(self.login_url, {
            "Email": "q@q.ru",
            "Password": "test"
        })

        self.assertEqual(response_login.url, self.profile_url)

        response = self.client.post(reverse('test_view', args=[test.id]), {
            'evaluation': '',
            f'q{question.id}a{answer.id}': 'on'
        })

        applicaton = models.SitterApplication.objects.filter(user=self.sitter).first()
        sitter_education = models.SitterEducation.objects.filter(education=education,
                                                                 sitterApplication=applicaton).first()

        self.assertEqual(response.url, reverse('sitter_application'))
        self.assertEqual(applicaton, self.application)
        self.assertEqual(sitter_education.result, 100)
