# Generated by Django 3.0.6 on 2020-06-08 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financing', '0002_auto_20200524_1555'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investment',
            name='checked',
            field=models.BooleanField(default=False, verbose_name='Revisado'),
        ),
        migrations.AlterField(
            model_name='loan',
            name='checked',
            field=models.BooleanField(default=False, verbose_name='Revisado'),
        ),
    ]
