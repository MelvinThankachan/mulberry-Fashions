# Generated by Django 5.0.1 on 2024-04-25 07:34

import django.db.models.manager
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0016_category_deleted_at_category_is_deleted_and_more'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='product',
            managers=[
                ('approved_objects', django.db.models.manager.Manager()),
            ],
        ),
    ]
