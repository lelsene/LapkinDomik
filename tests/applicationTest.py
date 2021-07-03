from datetime import datetime
from django.test import TestCase
from django.urls import reverse
from SitterService import models
from django.contrib.auth.hashers import make_password


class ApplicationTest(TestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')
        self.applications_url = reverse('retreat_applications')

        self.owner = models.User.objects.create(
            email="owner@test.ru",
            password=make_password("test")
        )

        self.sitter = models.User.objects.create(
            email="sitter@test.ru",
            password=make_password("test"),
            type=models.User.Type.SITTER
        )

        response_login = self.client.post(self.login_url, {
            "Email": "owner@test.ru",
            "Password": "test"
        })

        self.assertEqual(response_login.url, self.profile_url)

        self.profile_owner = models.Profile.objects.create(
            user=self.owner,
            name="Owner",
            surname='OwnerSurname',
            sex=models.Sex.female,
            birthday=datetime.now().date(),
            city="Ульяновск",
            phoneNumber="+7(900)-123-45-67"
        )

        self.profile_sitter = models.Profile.objects.create(
            user=self.sitter,
            name="Sitter",
            surname='SitterSurname',
            sex=models.Sex.female,
            birthday=datetime.now().date(),
            city="Ульяновск",
            phoneNumber="+7(900)-123-45-67",
            price=500,
        )

        self.petType = models.PetType.objects.create(title='Type')

        self.profile_sitter.petTypes.add(self.petType)

        self.pet = models.Pet.objects.create(
            user=self.owner,
            name="Pet",
            age=1,
            sex='Женский',
            petType=self.petType,
        )

        self.application_create_url = reverse('retreat_application_create', args=[self.profile_sitter.id])

    def test_add_application_positive(self):
        response = self.client.post(self.application_create_url, {
            'createApplication': '',
            'pets': [self.pet.id],
            'dateFrom': "2020-12-12",
            'dateTo': "2020-12-13",
            'description': '',
        })

        application = models.RetreatApplication.objects.filter(owner=self.owner).first()

        self.assertEqual(response.url, self.applications_url)
        self.assertEqual(application.owner, self.owner)
        self.assertEqual(application.sitter, self.sitter)
        self.assertEqual(application.pets.filter().first(), self.pet)

    def test_add_application_negative(self):
        response = self.client.post(self.application_create_url, {
            'createApplication': '',
            'pets': [self.pet.id],
            'dateFrom': "2020-12-12",
            'dateTo': "2020-12-12",
            'description': '',
        })

        application = models.RetreatApplication.objects.filter(owner=self.owner)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(getattr(response, 'request')['PATH_INFO'], self.application_create_url)
        self.assertEqual(len(application), 0)

    def test_delete_application_positive(self):
        response = self.client.post(self.application_create_url, {
            'createApplication': '',
            'pets': [self.pet.id],
            'dateFrom': "2020-12-12",
            'dateTo': "2020-12-13",
            'description': '',
        })

        application = models.RetreatApplication.objects.filter(owner=self.owner).first()

        self.assertEqual(response.url, self.applications_url)

        response = self.client.post(self.applications_url, {
            'retreatDelete': application.id,
        })

        application = models.RetreatApplication.objects.filter(id=application.id)

        self.assertEqual(response.url, self.applications_url)
        self.assertEqual(len(application), 0)

    def test_view_application_positive(self):
        response = self.client.post(self.application_create_url, {
            'createApplication': '',
            'pets': [self.pet.id],
            'dateFrom': "2020-12-12",
            'dateTo': "2020-12-13",
            'description': '',
        })

        application = models.RetreatApplication.objects.filter(owner=self.owner).first()

        self.assertEqual(response.url, self.applications_url)

        applications_view_url = reverse('retreat_application_view', args=[application.id])

        response = self.client.get(applications_view_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(applications_view_url, getattr(response, 'request')['PATH_INFO'])

    def test_accept_application_positive(self):
        response = self.client.post(self.application_create_url, {
            'createApplication': '',
            'pets': [self.pet.id],
            'dateFrom': "2020-12-12",
            'dateTo': "2020-12-13",
            'description': '',
        })

        application = models.RetreatApplication.objects.filter(owner=self.owner).first()

        self.assertEqual(response.url, self.applications_url)

        response_login = self.client.post(self.login_url, {
            "Email": "sitter@test.ru",
            "Password": "test"
        })

        self.assertEqual(response_login.url, self.profile_url)

        response = self.client.post(self.applications_url, {
            'retreatAccept': application.id
        })

        application = models.RetreatApplication.objects.filter(id=application.id).first()

        self.assertEqual(self.applications_url, response.url)
        self.assertEqual(application.status, models.Status.ACCEPTED)

    def test_reject_application_positive(self):
        response = self.client.post(self.application_create_url, {
            'createApplication': '',
            'pets': [self.pet.id],
            'dateFrom': "2020-12-12",
            'dateTo': "2020-12-13",
            'description': '',
        })

        application = models.RetreatApplication.objects.filter(owner=self.owner).first()

        self.assertEqual(response.url, self.applications_url)

        response_login = self.client.post(self.login_url, {
            "Email": "sitter@test.ru",
            "Password": "test"
        })

        self.assertEqual(response_login.url, self.profile_url)

        response = self.client.post(self.applications_url, {
            'retreatReject': application.id
        })

        application = models.RetreatApplication.objects.filter(id=application.id).first()

        self.assertEqual(self.applications_url, response.url)
        self.assertEqual(application.status, models.Status.REJECTED)
