from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.middleware import get_user
from django.contrib.auth.models import AnonymousUser

class JWTAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        jwt_authenticator = JWTAuthentication()

        # Extract the token from the cookies
        access_token = request.COOKIES.get('access_token')

        if access_token:
            try:
                # Validate the token and set the user in the request
                validated_token = jwt_authenticator.get_validated_token(access_token)
                user = jwt_authenticator.get_user(validated_token)
                request.user = user
                print(f"Authenticated user: {user}")
            except Exception as e:
                # Handle exceptions related to token validation
                print(f"Token validation failed: {e}")
                request.user = AnonymousUser()

        # If no token is found, set the user to anonymous
        else:
            request.user = get_user(request)