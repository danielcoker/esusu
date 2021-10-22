# Generated by Django 3.2.8 on 2021-10-22 00:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0003_alter_membership_created_at'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='membership',
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Cycle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cycle_number', models.IntegerField(blank=True, null=True, verbose_name='cycle number')),
                ('start_date', models.DateField(verbose_name='start date')),
                ('end_date', models.DateField(verbose_name='end date')),
                ('next_saving_date', models.DateField(blank=True, null=True, verbose_name='next saving date')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cycles', to='groups.group')),
            ],
        ),
    ]
