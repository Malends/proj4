# Generated by Django 3.2.4 on 2021-06-23 08:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0004_review_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='review',
            options={'permissions': (('can_moderate_views', 'Can moderate views'),)},
        ),
    ]