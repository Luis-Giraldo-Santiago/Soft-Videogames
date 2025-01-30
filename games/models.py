from django.db import models

class Games(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    developer = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    genres = models.TextField()
    release_date = models.DateField()
    price_steam = models.FloatField()
    rating = models.FloatField()
    num_reviews = models.IntegerField()


    def __str__(self):
        return self.title
