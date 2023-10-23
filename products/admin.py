# Register your models here.
from django.contrib import admin
from .models import Product

# model hinzufuegen damit es auf der admin-seite sichtbar ist
admin.site.register(Product)

