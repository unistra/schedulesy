# Generated by Django 2.1.11 on 2019-08-30 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ade_api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DisplayType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Display type',
                'verbose_name_plural': 'Display types',
            },
        ),
    ]
