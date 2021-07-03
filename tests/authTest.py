from django.test import TestCase
from django.urls import reverse
from SitterService import models
from django.contrib.auth.hashers import check_password, make_password


class AuthTest(TestCase):
    def setUp(self):
        self.registration_url = reverse('registration')
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')

    def test_registration_positive(self):
        response = self.client.post(self.registration_url, {
            "Email": "test@test.ru",
            "Password": "test"
        })

        user = models.User.objects.filter(email="test@test.ru").first()

        self.assertEqual(response.url, self.profile_url)
        self.assertEqual(True, check_password("test", user.password))

    def test_registration_negative(self):
        count_before = len(list(models.User.objects.all()))
        response = self.client.post(self.registration_url)
        count_after = len(list(models.User.objects.all()))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(count_before, count_after)

    def test_login_positive(self):
        models.User.objects.create(
            email="test@test.ru",
            password=make_password("test")
        )

        response = self.client.post(self.login_url, {
            "Email": "test@test.ru",
            "Password": "test"
        })

        user = models.User.objects.filter(email="test@test.ru").first()
        token = getattr(response, 'cookies')['token'].value

        self.assertEqual(response.url, self.profile_url)
        self.assertEqual(user.token, token)

    def test_login_negative(self):
        models.User.objects.create(
            email="test@test.ru",
            password=make_password("test")
        )

        response = self.client.post(self.login_url)
        user = models.User.objects.filter(email="test@test.ru").first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.token, '')
