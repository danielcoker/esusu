# Generated by Django 3.2.8 on 2021-10-23 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bank',
            name='is_default',
            field=models.BooleanField(default=False, verbose_name='default bank'),
        ),
    ]
