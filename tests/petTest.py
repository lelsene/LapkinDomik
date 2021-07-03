from datetime import datetime
from django.test import TestCase
from django.urls import reverse
from SitterService import models
from django.contrib.auth.hashers import make_password


class PetTest(TestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')

        self.user = models.User.objects.create(
            email="test@test.ru",
            password=make_password("test")
        )

        response_login = self.client.post(self.login_url, {
            "Email": "test@test.ru",
            "Password": "test"
        })

        self.assertEqual(response_login.url, self.profile_url)

        self.profile = models.Profile.objects.create(
            user=self.user,
            name="TestName",
            surname='TestSurname',
            sex=models.Sex.female,
            birthday=datetime.now().date(),
            city="Ульяновск",
            phoneNumber="+7(900)-123-45-67"
        )

        self.petTypes = models.PetType.objects.bulk_create([
            models.PetType(title="Type1"),
            models.PetType(title="Type2")
        ])

    def test_add_pet_positive(self):
        response = self.client.post(self.profile_url, {
            "petSave": '',
            "petName_": "TestPetName",
            "petAge_": 1,
            "petSex_": "Женский",
            "petType_": self.petTypes[0].title,
            "petDescription_": "TestDescription"
        })

        pet = models.Pet.objects.filter(name="TestPetName").first()

        self.assertEqual(response.url, self.profile_url)
        self.assertEqual(pet.name, "TestPetName")
        self.assertEqual(pet.age, 1)
        self.assertEqual(pet.sex, "Женский")
        self.assertEqual(pet.petType.title, self.petTypes[0].title)
        self.assertEqual(pet.description, "TestDescription")

    def test_add_pet_negative(self):
        response = self.client.post(self.profile_url, {
            "petSave": ''
        })

        pets = models.Pet.objects.all()
        self.assertEqual(response.url, self.profile_url)
        self.assertEqual(len(pets), 0)

    def test_change_pet_positive(self):
        response = self.client.post(self.profile_url, {
            "petSave": '',
            "petName_": "TestPetName",
            "petAge_": 1,
            "petSex_": "Женский",
            "petType_": self.petTypes[0].title,
            "petDescription_": "TestDescription"
        })

        pet_before = models.Pet.objects.filter(name="TestPetName").first()

        self.assertEqual(response.url, self.profile_url)

        response_change = self.client.post(self.profile_url, {
            "petSave": str(pet_before.id),
            f"petName_{pet_before.id}": "ChangePetName",
            f"petAge_{pet_before.id}": 2,
            f"petSex_{pet_before.id}": "Мужской",
            f"petType_{pet_before.id}": self.petTypes[1].title,
            f"petDescription_{pet_before.id}": "ChangeDescription"
        })

        pet_after = models.Pet.objects.filter(id=pet_before.id).first()

        self.assertEqual(response_change.url, self.profile_url)
        self.assertNotEqual(pet_after.name, pet_before.name)
        self.assertNotEqual(pet_after.age, pet_before.age)
        self.assertNotEqual(pet_after.sex, pet_before.sex)
        self.assertNotEqual(pet_after.petType.title, pet_before.petType.title)
        self.assertNotEqual(pet_after.description, pet_before.description)

    def test_delete_pet_positive(self):
        response = self.client.post(self.profile_url, {
            "petSave": '',
            "petName_": "TestPetName",
            "petAge_": 1,
            "petSex_": "Женский",
            "petType_": self.petTypes[0].title,
            "petDescription_": "TestDescription"
        })

        pet_before = models.Pet.objects.filter(name="TestPetName").first()

        self.assertEqual(response.url, self.profile_url)

        response_delete = self.client.post(self.profile_url, {
            "petDelete": str(pet_before.id),
        })

        pet_after = models.Pet.objects.filter(id=pet_before.id)

        self.assertEqual(response_delete.url, self.profile_url)
        self.assertEqual(len(pet_after), 0)
