# Generated by Django 3.0.5 on 2021-05-24 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='date_created',
        ),
        migrations.AlterField(
            model_name='product',
            name='crypto',
            field=models.CharField(default='BTC', max_length=200, null=True),
        ),
    ]
