import models

from factory.django import DjangoModelFactory
from django.contrib.auth.models import User


class SpecialityFactory(DjangoModelFactory):
    class Meta:
        model = models.Speciality

    name = 'Офтальмолог'


class DoctorFactory(DjangoModelFactory):
    class Meta:
        model = models.Doctor

    first_name = 'Иван'
    last_name = 'Иванов'
    second_name = 'Иванович'


class ReviewFactory(DjangoModelFactory):
    class Meta:
        model = models.Review

    raw_review = 'Некоторый  !  текст'
    edited_review = 'Некоторый! текст'
    ip_address = '255.255.255.255'


class ForbiddenFactory(DjangoModelFactory):
    class Meta:
        model = models.Forbidden

    word = 'слово'


class ExceptedFactory(DjangoModelFactory):
    class Meta:
        model = models.Excepted

    word = 'другоеслово'


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = 'user'