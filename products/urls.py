from django.urls import path, include
from . import views

urlpatterns = [
    # hinzufuegen einer View mit dem Namen product_list
    # views.product_list ist also das gewünschte Ziel,
    # wenn jemand 'http://127.0.0.1:8000/' aufruft
    #path('', views.product_data, name='product_data'),
    path('username_exists_form', views.add_prod, name='add_prod'),
    path('add_product', views.add_prod, name='add_prod'),
]