from django.db import models

# Create your models here.

class Word(models.Model):
    word = models.CharField(max_length=50)
    player = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)


class UserPlay(models.Model):
    name = models.CharField(max_length=200)
    word = models.CharField(max_length=200)
    meaning = models.TextField()
