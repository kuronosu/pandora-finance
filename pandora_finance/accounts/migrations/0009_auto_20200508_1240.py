# Generated by Django 3.0.6 on 2020-05-08 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_auto_20200508_1239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.PositiveSmallIntegerField(choices=[(2, 'cliente'), (1, 'empleado')]),
        ),
    ]
