import re

from django.db import models
from django.contrib.auth.models import User



class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    class Meta:
        abstract = True


class Speciality(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')

    def __str__(self):
        return self.name


class Doctor(models.Model):
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    second_name = models.CharField(max_length=100, verbose_name='Отчество')
    speciality = models.ManyToManyField(Speciality, verbose_name='Специальность')

    def __str__(self):
        return '{} {} {}'.format(self.last_name, self.first_name, self.second_name)


class Review(TimeStampMixin):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Пользователь')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name='Врач')
    raw_review = models.TextField(verbose_name='Текст пользователя')
    edited_review = models.TextField(blank=True, verbose_name='Отредактированный текст')
    ip_address = models.CharField(max_length=20, verbose_name='IP адресс')

    class Meta:
        permissions = (('can_moderate_views', 'Can moderate views'),)

    def __str__(self):
        return self.edited_review[:50] if len(self.edited_review) != 0 else self.raw_review

    @staticmethod
    def check_cases(review):
        count_upper = 0
        for i in review:
            if i.isupper():
                count_upper += 1
            else:
                count_upper = 0
            if count_upper != 6:
                continue
            edited = review.capitalize()
            edited = re.sub(r'([.!?] +)(\w)', Review.upper_match, edited)
            return edited
        return review

    @staticmethod
    def upper_match(match):
        return match.group(1) + match.group(2).upper()

    @staticmethod
    def trim_match(match):
        return match.group(1)[0] + ' '

    @staticmethod
    def check_spaces_and_punctuation(review):
        edited = re.sub(r' *([.,!?:;]+) *', Review.trim_match, review)
        return edited

    def edit_review(self):
        edited = self.check_spaces_and_punctuation(self.raw_review)
        self.edited_review = self.check_cases(edited)
        self.save()


class Forbidden(models.Model):
    word = models.CharField(max_length=50, verbose_name='Слово')

    def __str__(self):
        return self.word


class Excepted(models.Model):
    word = models.CharField(max_length=50, verbose_name='Слово')

    def __str__(self):
        return self.word
