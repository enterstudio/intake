# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-07 19:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_accounts', '0014_long_and_short_confirmation_messages'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='notify_on_weekends',
            field=models.BooleanField(default=False),
        ),
    ]