# Generated by Django 5.0.1 on 2024-05-07 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0013_order_coupon_order_discount_alter_order_total_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='discount',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
    ]
