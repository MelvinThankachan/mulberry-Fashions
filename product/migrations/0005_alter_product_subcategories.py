# Generated by Django 5.0.1 on 2024-02-21 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_productimage_priority'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='subcategories',
            field=models.ManyToManyField(blank=True, null=True, related_name='subcategory_products', to='product.category'),
        ),
    ]