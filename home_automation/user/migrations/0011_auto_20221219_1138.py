# Generated by Django 3.1.5 on 2022-12-19 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_auto_20221219_1127'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='email_verified',
            field=models.BooleanField(default=False, help_text='Designates whether this user email is verified. ', verbose_name='email verified'),
        ),
        migrations.AddField(
            model_name='myuser',
            name='mobile_verified',
            field=models.BooleanField(default=False, help_text='Designates whether this user mobile is verified. ', verbose_name='mobile verified'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active'),
        ),
    ]