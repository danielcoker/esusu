# Generated by Django 3.2.8 on 2021-10-25 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0005_remove_card_account_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='reference',
            field=models.CharField(default='T451753668993135', max_length=255, verbose_name='transaction reference'),
            preserve_default=False,
        ),
    ]