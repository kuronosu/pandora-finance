# Generated by Django 3.0.6 on 2020-05-24 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financing', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investment',
            name='end_date',
            field=models.DateField(blank=True, null=True, verbose_name='Fecha de término'),
        ),
        migrations.AlterField(
            model_name='investment',
            name='start_date',
            field=models.DateField(blank=True, null=True, verbose_name='Fecha de inicio'),
        ),
        migrations.AlterField(
            model_name='loan',
            name='end_date',
            field=models.DateField(blank=True, null=True, verbose_name='Fecha de término'),
        ),
        migrations.AlterField(
            model_name='loan',
            name='start_date',
            field=models.DateField(blank=True, null=True, verbose_name='Fecha de inicio'),
        ),
    ]