# Generated by Django 3.1.5 on 2022-10-06 09:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_remove_usermodel_user_password'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usermodel',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='usermodel',
            name='is_admin',
        ),
        migrations.RemoveField(
            model_name='usermodel',
            name='last_login',
        ),
        migrations.RemoveField(
            model_name='usermodel',
            name='password',
        ),
        migrations.AddField(
            model_name='usermodel',
            name='user_password',
            field=models.CharField(default=1, error_messages={'unique': 'Please password must be between 8-16 characters.'}, help_text='Required 16 maximum characters or minimum 8.', max_length=16, validators=[django.core.validators.MinLengthValidator(8)], verbose_name='user password'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='usermodel',
            name='user_email',
            field=models.EmailField(blank=True, error_messages={'unique': 'A user with that email address  already exists.'}, max_length=254, null=True, unique=True, verbose_name='user email'),
        ),
    ]