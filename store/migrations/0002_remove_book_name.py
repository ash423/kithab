# Generated by Django 4.2.3 on 2023-07-18 11:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='name',
        ),
    ]
