# Generated by Django 4.2.4 on 2023-08-16 10:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='department',
            table='department',
        ),
        migrations.AlterModelTable(
            name='employee',
            table='employee',
        ),
    ]