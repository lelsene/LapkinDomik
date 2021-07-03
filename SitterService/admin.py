from django.contrib import admin
from .models import User, PetType, Profile, Education, Test, Question, Answer, SitterApplication, SitterEducation, Pet, \
    RetreatApplication

admin.site.register(User)
admin.site.register(PetType)
admin.site.register(Profile)
admin.site.register(Education)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(SitterApplication)
admin.site.register(SitterEducation)
admin.site.register(Pet)
admin.site.register(RetreatApplication)
