import jwt
from django.conf import settings
from rest_framework import permissions
import os

class IsAuthenticatedCookie(permissions.BasePermission):
    """
    Custom permission class to check if the user is authenticated via cookies.
    """

    def has_permission(self, request, view):
        # Check for access token in the cookie
        access_token = request.COOKIES.get("access_token")

        # If there's no token in cookies, check Authorization header
        if not access_token:
            authorization_header = request.headers.get("Authorization")
            access_token = (
                authorization_header.replace("Bearer ", "")
                if authorization_header
                else None
            )

        # Validate the access token (e.g., using a library like PyJWT)
        if not access_token:
            return False

        try:
            decoded_token = jwt.decode(
                access_token,
                key=settings.SIMPLE_JWT["SIGNING_KEY"],
                algorithms=[settings.SIMPLE_JWT["ALGORITHM"]],
            )

            request.user_id = decoded_token["user_id"]
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

        return True
