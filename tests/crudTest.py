from datetime import datetime
from django.test import TestCase
from django.urls import reverse
from SitterService import models
from django.contrib.auth.hashers import make_password


class CrudTest(TestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')
        self.educations_url = reverse('educations')
        self.tests_url = reverse('tests')

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

    def test_add_education_positive(self):
        educations_before = list(models.Education.objects.all())
        response = self.client.post(self.educations_url, {
            'educationAdd': ''
        })
        educations_after = list(models.Education.objects.all())

        self.assertEqual(self.educations_url, response.url)
        self.assertNotEqual(len(educations_before), len(educations_after))

    def test_change_education_positive(self):
        education_before = models.Education.objects.create(
            title="TestEducation",
            source='TestSource',
            description='TestDescription'
        )

        response = self.client.post(self.educations_url, {
            'educationUpdate': education_before.id,
            f'Title_{education_before.id}': "ChangeEducation",
            f'Source_{education_before.id}': "ChangeSource",
            f'Description_{education_before.id}': "ChangeDescription",
        })

        education_after = models.Education.objects.filter(id=education_before.id).first()
        self.assertEqual(self.educations_url, response.url)
        self.assertNotEqual(education_after.title, education_before.title)
        self.assertNotEqual(education_after.source, education_before.source)
        self.assertNotEqual(education_after.description, education_before.description)

    def test_delete_education_positive(self):
        education = models.Education.objects.create(
            title="TestEducation",
            source='TestSource',
            description='TestDescription'
        )

        response = self.client.post(self.educations_url, {
            'educationDelete': education.id
        })

        education = list(models.Education.objects.filter(id=education.id))

        self.assertEqual(self.educations_url, response.url)
        self.assertEqual(len(education), 0)

    def test_add_test_positive(self):
        response = self.client.post(self.educations_url, {
            'educationAdd': ''
        })
        self.assertEqual(self.educations_url, response.url)

        tests_before = list(models.Test.objects.all())
        response = self.client.post(self.tests_url, {
            'testAdd': ''
        })
        tests_after = list(models.Test.objects.all())

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(len(tests_before), len(tests_after))

    def test_change_test_positive(self):
        education = models.Education.objects.create(
            title="TestEducation",
            source='TestSource',
            description='TestDescription'
        )

        test_before = models.Test.objects.create(
            title="Test",
            education=education
        )

        response = self.client.post(self.tests_url, {
            'testUpdate': test_before.id,
            f'Title_{test_before.id}': "ChangeTest",
            f'Education_{test_before.id}': "TestEducation",
        })

        test_after = models.Test.objects.filter(id=test_before.id).first()

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(test_before.title, test_after.title)

    def test_delete_test_positive(self):
        education = models.Education.objects.create(
            title="TestEducation",
            source='TestSource',
            description='TestDescription'
        )

        test = models.Test.objects.create(
            title="Test",
            education=education
        )

        response = self.client.post(self.tests_url, {
            'testDelete': test.id,
        })

        test = list(models.Test.objects.filter(id=test.id))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(test), 0)
