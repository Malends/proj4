import random

from django.core.management.base import BaseCommand
from reviews.models import Doctor, Speciality


class Command(BaseCommand):
    help = 'Generates n random entries in Doctors'

    def add_arguments(self, parser):
        parser.add_argument('amount', type=int)

    def handle(self, *args, **options):
        for _ in range(options['amount']):
            first_name = random.randint(1, 10000)
            last_name = random.randint(1, 10000)
            second_name = random.randint(1, 10000)
            speciality = Speciality.objects.get(pk=random.randint(1, 5))
            entry = Doctor.objects.create(first_name=first_name, last_name=last_name, second_name=second_name)
            entry.save()
            entry.speciality.add(speciality)
            entry.save()

        self.stdout.write('{} entries are successfully generated'.format(options['amount']))
