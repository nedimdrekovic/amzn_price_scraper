from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product # model mit dem Formular erstellt werden soll
        fields = ('title', 'url',)

