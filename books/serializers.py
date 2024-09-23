from rest_framework import serializers
from .models import Author, Book, UserFavorite
from django.contrib.auth.models import User

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    authors = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), many=True)

    class Meta:
        model = Book
        fields = '__all__'

    def create(self, validated_data):
        authors_data = validated_data.pop('authors')
        book = Book.objects.create(**validated_data)
        book.authors.set(authors_data)
        return book

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']

class UserFavoriteSerializer(serializers.ModelSerializer):
    # book = BookSerializer()
    book_id = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), source='book')
    class Meta:
        model = UserFavorite
        fields = ['id', 'book_id']