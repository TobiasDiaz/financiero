# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-29 23:01
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contables', '0007_auto_20171129_2243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaccion',
            name='fecha',
            field=models.DateField(default=datetime.datetime.now),
        ),
    ]
