from django.urls import path
from . import authView, profileView, sitterView, crudView, applicationView, adminView

urlpatterns = [
    path('registration', authView.registration, name='registration'),
    path('login', authView.login, name='login'),
    path('logout', authView.logout, name='logout'),

    path('profile', profileView.profile, name='profile'),
    path('profile/<int:user_id>', profileView.user_profile, name='user_profile'),

    path('', profileView.main, name='main'),

    path('retreat_applications', applicationView.retreat_applications, name='retreat_applications'),
    path('retreat_application/view/<int:app_id>', applicationView.retreat_application_view,
         name='retreat_application_view'),
    path('retreat_application/create/<int:sitter_id>', applicationView.retreat_application_create,
         name='retreat_application_create'),

    path('users', adminView.users, name='users'),

    path('educations', crudView.educations, name='educations'),
    path('tests', crudView.tests, name='tests'),
    path('questions', crudView.questions, name='questions'),
    path('answers', crudView.answers, name='answers'),

    path('sitters', sitterView.sitters, name='sitters'),
    path('sitter/educations', sitterView.educations_view, name='educations_view'),
    path('sitter/education/<int:education_id>', sitterView.education_view, name='education_view'),
    path('sitter/test/<int:test_id>', sitterView.test_view, name='test_view'),
    path('sitter/applications', sitterView.sitter_applications, name='sitter_applications'),
    path('sitter/application', sitterView.sitter_application, name='sitter_application'),
]
