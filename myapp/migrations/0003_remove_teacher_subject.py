# Generated by Django 5.1.5 on 2025-02-05 08:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_alter_student_year_section'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='subject',
        ),
    ]
