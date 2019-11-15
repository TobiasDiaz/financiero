# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-23 01:27
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contables', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('correlativo', models.IntegerField(default=1, unique=True, validators=[django.core.validators.MaxValueValidator(12), django.core.validators.MinValueValidator(1)])),
                ('nombre', models.CharField(max_length=49)),
            ],
            options={
                'verbose_name': 'Mes',
                'verbose_name_plural': 'Meses',
            },
        ),
    ]