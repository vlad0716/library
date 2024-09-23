from rest_framework import viewsets, filters, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .permissions import IsAuthenticatedCookie
from rest_framework.decorators import action
from django.contrib.auth.models import User
from .models import Author, Book, UserFavorite
from .serializers import AuthorSerializer, BookSerializer, UserSerializer, UserFavoriteSerializer
from rest_framework_simplejwt.tokens import RefreshToken
import datetime
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

class RegisterView(views.APIView):
    permission_classes = []

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_password(request.data['password'])  # Set the password correctly
        user.save()

        return Response(status=status.HTTP_201_CREATED)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh_token = response.data['refresh']
        access_token = response.data['access']

        max_age = datetime.timedelta(days=1)

        response.set_cookie(
            key="refresh_token",
            value=str(refresh_token),
            httponly=False,
            secure=True,
            max_age=max_age,
            samesite="None",
        )

        response.set_cookie(
            key="access_token",
            value=str(access_token),
            httponly=False,
            secure=True,
            max_age=max_age,
            samesite="None",
        )

        return response

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get('refresh_token')
        if refresh:
            request.data['refresh'] = refresh
        response = super().post(request, *args, **kwargs)
        new_access_token = response.data['access']
        max_age = datetime.timedelta(days=1)

        # Update the access token in the cookie
        response.set_cookie(
            key='access_token', 
            value=str(new_access_token), 
            httponly=True,
            secure=True,
            max_age=max_age,
            samesite="None",
        )

        return response

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticatedCookie]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticatedCookie]
        return super().get_permissions()

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedCookie]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'authors__name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticatedCookie]
        return super().get_permissions()

class UserFavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = UserFavoriteSerializer
    permission_classes = [IsAuthenticatedCookie]

    def get_queryset(self):
        return UserFavorite.objects.filter(user=self.request.user_id)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticatedCookie])
    def add_favorite(self, request, *args, **kwargs):
        user = request.user
        book_id = request.data.get('book_id')
        book = Book.objects.get(id=book_id)

        if UserFavorite.objects.filter(user=user, book=book).exists():
            return Response({'detail': 'Already added to favorites'}, status=status.HTTP_400_BAD_REQUEST)

        if UserFavorite.objects.filter(user=user).count() >= 20:
            return Response({'detail': 'Favorite list can only contain up to 20 books'}, status=status.HTTP_400_BAD_REQUEST)

        UserFavorite.objects.create(user=user, book=book)
        return Response({'detail': 'Added to favorites'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticatedCookie])
    def remove_favorite(self, request, *args, **kwargs):
        user = request.user
        book_id = request.data.get('book_id')
        book = Book.objects.get(id=book_id)

        favorite = UserFavorite.objects.filter(user=user, book=book)
        if favorite.exists():
            favorite.delete()
            return Response({'detail': 'Removed from favorites'}, status=status.HTTP_200_OK)

        return Response({'detail': 'Book not in favorites'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticatedCookie])
    def recommendations(self, request, *args, **kwargs):
        user = request.user
        favorite_books = UserFavorite.objects.filter(user=user).values_list('book_id', flat=True)

        if not favorite_books:
            return Response({'detail': 'No favorite books'}, status=status.HTTP_400_BAD_REQUEST)

        favorite_books = Book.objects.filter(id__in=favorite_books)
        return self.get_recommendations(favorite_books)

    def get_recommendations(self, favorite_books):
        # Example Contents-Based Filtering: Finds books with similar authors
        all_books = Book.objects.all()
        favorite_titles = [book.title for book in favorite_books]

        # Creating DataFrame for the Book and Author
        books = list(all_books)
        data = {
            'title': [book.title for book in books],
            'authors': [' '.join([author.name for author in book.authors.all()]) for book in books]
        }
        df_books = pd.DataFrame(data)

        # Count Vectorizer
        count = CountVectorizer()
        count_matrix = count.fit_transform(df_books['authors'])

        # Creating Similarity Matrix
        cosine_sim = cosine_similarity(count_matrix, count_matrix)

        # Calculate similarity scores for favorite books
        similar_books = []

        for book in favorite_books:
            idx = df_books[df_books['title'] == book.title].index[0]
            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores_sorted = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores_sorted = [i[0] for i in sim_scores_sorted[1:6]]

            similar_books.extend([books[i] for i in sim_scores_sorted])

        similar_books = list(set(similar_books) - set(favorite_books))  # Remove already favorite books
        similar_books = sorted(similar_books, key=lambda book: book.average_rating, reverse=True)[:5]  # Top 5

        serializer = BookSerializer(similar_books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    