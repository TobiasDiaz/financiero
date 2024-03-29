# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-29 11:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contables', '0004_cuenta_totalcuenta'),
    ]

    operations = [
        migrations.CreateModel(
            name='CuentaBalanceGeneral',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, unique=True)),
                ('totalCuenta', models.FloatField(default=0.0)),
            ],
            options={
                'verbose_name': 'Cuenta Balance General',
                'verbose_name_plural': 'Cuentas Balance General',
            },
        ),
    ]
