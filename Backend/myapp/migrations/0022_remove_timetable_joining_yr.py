# Generated by Django 4.0.6 on 2024-04-14 20:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0021_alter_timetable_joining_yr'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timetable',
            name='joining_yr',
        ),
    ]
