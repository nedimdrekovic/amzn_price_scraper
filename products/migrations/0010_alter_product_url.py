# Generated by Django 4.2.6 on 2023-10-23 12:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_alter_product_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='url',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.product'),
        ),
    ]