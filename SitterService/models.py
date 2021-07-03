from datetime import datetime
from django.db import models


class Sex(models.TextChoices):
    male = 'Мужской'
    female = 'Женский'


class User(models.Model):
    email = models.CharField(max_length=254, unique=True)
    password = models.CharField(max_length=128)
    token = models.CharField(max_length=254, default='', blank=True)

    class Type(models.TextChoices):
        ADMIN = 'Admin'
        SITTER = 'Sitter'
        OWNER = 'Owner'

    type = models.CharField(
        max_length=7,
        choices=Type.choices,
        default='Owner'
    )

    def __str__(self):
        return self.email


class PetType(models.Model):
    title = models.CharField(max_length=254)

    def __str__(self):
        return self.title


def user_directory_path(instance, filename):
    return f'static/images/{instance.user.id}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.{filename.split(".")[-1]}'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=254)
    surname = models.CharField(max_length=254)
    birthday = models.DateField()

    sex = models.CharField(
        max_length=7,
        choices=Sex.choices
    )

    description = models.TextField(default='', blank=True)
    image = models.ImageField(upload_to=user_directory_path, default='images/profile_image.jpg')
    city = models.CharField(max_length=254)
    price = models.IntegerField(default=0)
    phoneNumber = models.CharField(max_length=17)
    petTypes = models.ManyToManyField(PetType, blank=True)

    def __str__(self):
        return " ".join([self.name, self.surname])


class Education(models.Model):
    title = models.CharField(max_length=254)
    source = models.CharField(max_length=254)
    description = models.TextField(default='', blank=True)

    def __str__(self):
        return self.title


class Test(models.Model):
    title = models.CharField(max_length=254)
    education = models.OneToOneField(Education, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Question(models.Model):
    title = models.CharField(max_length=254)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Answer(models.Model):
    title = models.CharField(max_length=254)
    isRight = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Status(models.TextChoices):
    ACCEPTED = 'Принята'
    REJECTED = 'Отклонена'
    PROCESSING = 'На рассмотрении'


class SitterApplication(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default='На рассмотрении'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email + " " + self.date.__str__()


class SitterEducation(models.Model):
    education = models.ForeignKey(Education, on_delete=models.CASCADE)
    sitterApplication = models.ForeignKey(SitterApplication, on_delete=models.CASCADE)
    result = models.IntegerField(default=0)

    def __str__(self):
        return self.sitterApplication.user.email + " " + self.education.title


class Pet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=254)
    age = models.IntegerField()

    sex = models.CharField(
        max_length=7,
        choices=Sex.choices
    )

    description = models.TextField(default='', blank=True)
    image = models.ImageField(upload_to=user_directory_path, default='images/pet_image.png')
    petType = models.ForeignKey(PetType, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email + " " + self.name


class RetreatApplication(models.Model):
    owner = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              related_name='+')
    sitter = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='+')
    dateFrom = models.DateField()
    dateTo = models.DateField()
    description = models.TextField(default='', blank=True)
    totalCost = models.FloatField(default=0)
    pets = models.ManyToManyField(Pet)
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default='На рассмотрении'
    )

    def __str__(self):
        return self.owner.email + " " + self.dateFrom.__str__()
