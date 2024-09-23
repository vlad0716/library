from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from books.views import AuthorViewSet, BookViewSet, UserFavoriteViewSet, RegisterView, CustomTokenObtainPairView, CustomTokenRefreshView

router = DefaultRouter()
router.register(r'authors', AuthorViewSet)
router.register(r'books', BookViewSet)
router.register(r'favorites', UserFavoriteViewSet, basename='favorite')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterView.as_view(), name='register'),
]