# Generated by Django 5.0.1 on 2024-03-04 17:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0014_product_is_deleted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='is_deleted',
        ),
    ]