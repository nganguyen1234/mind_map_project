from django.db import models

# Create your models here.
class Text(models.Model):
    content = models.CharField(max_length = 200)