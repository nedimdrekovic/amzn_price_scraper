from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # hinzufuegen einer View mit dem Namen product_list
    # views.product_list ist also das gewünschte Ziel,
    # wenn jemand 'http://127.0.0.1:8000/' aufruft
    #path('', views.product_data, name='product_data'),
    #path('', views.add_prod, name='add_prod'),
    path('add_product', views.add_prod, name='add_prod'),
    path('', views.xy, name='xy'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)