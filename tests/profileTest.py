import datetime
from django.test import TestCase
from django.urls import reverse
from SitterService import models
from django.contrib.auth.hashers import make_password


class ProfileTest(TestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')

    def test_change_owner_positive(self):
        user = models.User.objects.create(
            email="test@test.ru",
            password=make_password("test")
        )

        response_login = self.client.post(self.login_url, {
            "Email": "test@test.ru",
            "Password": "test"
        })

        self.assertEqual(response_login.url, self.profile_url)

        profile_before = models.Profile.objects.create(
            user=user,
            name="TestName",
            surname='TestSurname',
            sex=models.Sex.female,
            birthday=datetime.datetime.now().date(),
            city="Ульяновск",
            phoneNumber="+7(900)-123-45-67"
        )

        response_change = self.client.post(self.profile_url, {
            "profileSave": "",
            "name": "ChangedName",
            "surname": "ChangedSurname",
            "sex": 'Мужской',
            "birthday": datetime.datetime.now().date() - datetime.timedelta(days=365),
            "city": "Димитровград",
            "phone": "+7(900)-987-65-43"
        })

        profile_after = models.Profile.objects.filter(id=profile_before.id).first()

        self.assertEqual(response_change.url, self.profile_url)
        self.assertNotEqual(profile_before.name, profile_after.name)
        self.assertNotEqual(profile_before.surname, profile_after.surname)
        self.assertNotEqual(profile_before.sex, profile_after.sex)
        self.assertNotEqual(profile_before.birthday, profile_after.birthday)
        self.assertNotEqual(profile_before.city, profile_after.city)
        self.assertNotEqual(profile_before.phoneNumber, profile_after.phoneNumber)

    def test_change_sitter_positive(self):
        user = models.User.objects.create(
            email="test@test.ru",
            password=make_password("test"),
            type=models.User.Type.SITTER
        )

        response_login = self.client.post(self.login_url, {
            "Email": "test@test.ru",
            "Password": "test"
        })

        self.assertEqual(response_login.url, self.profile_url)

        petType1 = models.PetType.objects.create(title='PetType1')
        petType2 = models.PetType.objects.create(title='PetType2')

        profile_before = models.Profile.objects.create(
            user=user,
            name="TestName",
            surname='TestSurname',
            sex=models.Sex.female,
            birthday=datetime.datetime.now().date(),
            city="Ульяновск",
            phoneNumber="+7(900)-123-45-67",
            description='TestDescription',
            price=500,
        )

        profile_before.petTypes.add(petType1)

        response_change = self.client.post(self.profile_url, {
            "profileSave": "",
            "name": "ChangedName",
            "surname": "ChangedSurname",
            "sex": 'Мужской',
            "birthday": datetime.datetime.now().date() - datetime.timedelta(days=365),
            "city": "Димитровград",
            "phone": "+7(900)-987-65-43",
            "price": 1000,
            "description": "ChangedDescription",
            "petType": [petType2.title]
        })

        profile_after = models.Profile.objects.filter(id=profile_before.id).first()

        self.assertEqual(response_change.url, self.profile_url)
        self.assertNotEqual(profile_before.name, profile_after.name)
        self.assertNotEqual(profile_before.surname, profile_after.surname)
        self.assertNotEqual(profile_before.sex, profile_after.sex)
        self.assertNotEqual(profile_before.birthday, profile_after.birthday)
        self.assertNotEqual(profile_before.city, profile_after.city)
        self.assertNotEqual(profile_before.phoneNumber, profile_after.phoneNumber)
        self.assertNotEqual(profile_before.price, profile_after.price)
        self.assertNotEqual(profile_before.description, profile_after.description)
        self.assertNotEqual(profile_before.petTypes.all(), profile_after.petTypes.all())

    def test_view_profile_positive(self):
        user = models.User.objects.create(
            email="test@test.ru",
            password=make_password("test"),
            type=models.User.Type.SITTER
        )

        response_login = self.client.post(self.login_url, {
            "Email": "test@test.ru",
            "Password": "test"
        })

        self.assertEqual(response_login.url, self.profile_url)

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.profile_url, getattr(response, 'request')['PATH_INFO'])
