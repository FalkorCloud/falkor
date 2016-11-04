# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-02 04:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('falkor', '0004_auto_20161102_0356'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='editor_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='falkor.EditorType'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='editortype',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]