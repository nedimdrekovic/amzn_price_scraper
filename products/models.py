# Create your models here.
from django.conf import settings
from django.db import models
from django.utils import timezone

class Product(models.Model):
    #author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    img_url = models.URLField(default=None)
    title = models.CharField(max_length=200, default=None)
    url = models.URLField(default='')
    price = models.CharField(max_length=10, default=None)
    preferred_price = models.CharField(max_length=10, default=None)
    #preferred_price = models.DecimalField(default="", max_digits=6, decimal_places=2)
    # spaeter aendern
    #published_date = models.DateTimeField(blank=True, null=True)
    #published_date = models.CharField(max_length=100, null=True, default=None)

    def publish(self):
        #self.published_date = timezone.now()
        self.save()

    @staticmethod
    def print_instance_attributes():
        attributes = []
        for attribute in Product.__dict__.keys():
            if (not attribute.startswith('_')) and (attribute != 'id'):
                attributes.append(attribute)
        return attributes

    def __str__(self):
        return self.title