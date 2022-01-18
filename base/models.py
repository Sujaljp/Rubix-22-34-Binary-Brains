from django.db import models
from django.contrib.auth.models import User
from datetime import date


# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE , null=True)
    created = models.DateTimeField(auto_now_add=True)
    expirydate = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name