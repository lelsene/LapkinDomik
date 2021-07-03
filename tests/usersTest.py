from datetime import datetime
from django.test import TestCase
from django.urls import reverse
from SitterService import models
from django.contrib.auth.hashers import make_password


class UsersTest(TestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.users_url = reverse('users')
        self.profile_url = reverse('profile')

        self.user = models.User.objects.create(
            email="test@test.ru",
            password=make_password("test"),
            type=models.User.Type.ADMIN
        )

        models.User.objects.bulk_create([
            models.User(email="q@q.ru", password=make_password("test")),
            models.User(email="w@w.ru", password=make_password("test")),
        ])

        self.users = list(models.User.objects.filter().exclude(type=models.User.Type.ADMIN))

        self.profiles = [models.Profile.objects.create(
            user=user,
            name="Name" + str(user.id),
            surname='Surname',
            sex=models.Sex.female,
            birthday=datetime.now().date(),
            city="Ульяновск",
            phoneNumber="+7(900)-123-45-67",
        ) for user in self.users]

        self.profile_urls = [reverse('user_profile', args=[user.id]) for user in self.users]

        response_login = self.client.post(self.login_url, {
            "Email": "test@test.ru",
            "Password": "test"
        })

        self.assertEqual(response_login.url, self.profile_url)

    def test_view_user_positive(self):
        response = self.client.get(self.profile_urls[0])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.profile_urls[0], getattr(response, 'request')['PATH_INFO'])

    def test_delete_user_positive(self):
        response = self.client.post(self.users_url, {
            'userDelete': self.users[0].id
        })

        user = models.User.objects.filter(id=self.users[0].id)

        self.assertEqual(response.url, self.users_url)
        self.assertEqual(len(user), 0)
