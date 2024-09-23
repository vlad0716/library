from django.db import models
from django.contrib.auth.models import User

class Author(models.Model):
    name = models.CharField(max_length=255)
    image_url = models.URLField()
    about = models.TextField(blank=True)
    ratings_count = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    text_reviews_count = models.IntegerField(default=0)
    fans_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, blank=True, null=True)
    isbn13 = models.CharField(max_length=17, blank=True, null=True)
    language = models.CharField(max_length=100)
    average_rating = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    ratings_count = models.IntegerField(default=0)
    text_reviews_count = models.IntegerField(default=0)
    publication_date = models.DateField()
    original_publication_date = models.DateField()
    publisher = models.CharField(max_length=255)
    num_pages = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    authors = models.ManyToManyField(Author)

    def __str__(self):
        return self.title

class UserFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')
