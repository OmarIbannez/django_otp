# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('otpauth', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='otpuser',
            old_name='otp_token',
            new_name='secret_key',
        ),
    ]
