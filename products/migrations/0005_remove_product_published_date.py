# Generated by Django 4.1.2 on 2022-10-25 09:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_remove_product_author_remove_product_created_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='published_date',
        ),
    ]