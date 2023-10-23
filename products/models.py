# Create your models here.
from django.conf import settings
from django.db import models

class Product(models.Model):
    #author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='MEDIA_ROOT/')
    title = models.CharField(max_length=200, default=None)
    url = models.URLField(default=None)#, on_delete=models.CASCADE)
    price = models.CharField(max_length=10, default=None)
    preferred_price = models.CharField(max_length=10, default=None)

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