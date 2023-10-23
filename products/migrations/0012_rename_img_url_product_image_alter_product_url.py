# Generated by Django 4.2.6 on 2023-10-23 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_remove_product_image_product_img_url_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='img_url',
            new_name='image',
        ),
        migrations.AlterField(
            model_name='product',
            name='url',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product'),
        ),
    ]