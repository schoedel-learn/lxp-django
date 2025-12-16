"""
JWT Authentication for the LXP platform.

Provides token-based authentication for API access.
"""

import jwt
from datetime import datetime, timedelta, timezone

from django.conf import settings
from rest_framework import authentication, exceptions

from .models import User


class JWTAuthentication(authentication.BaseAuthentication):
    """
    JWT token authentication for Django REST Framework.
    """
    
    def authenticate(self, request):
        """
        Authenticate the request and return a tuple of (user, token) or None.
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None
        
        try:
            prefix, token = auth_header.split(' ')
        except ValueError:
            return None
        
        if prefix.lower() != 'bearer':
            return None
        
        return self._authenticate_credentials(token)
    
    def _authenticate_credentials(self, token):
        """
        Validate the JWT token and return the user.
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=['HS256']
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
        
        user_id = payload.get('user_id')
        if not user_id:
            raise exceptions.AuthenticationFailed('Invalid token payload')
        
        try:
            user = User.objects.get(pk=user_id, is_active=True)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')
        
        return (user, token)


def generate_access_token(user):
    """
    Generate a JWT access token for the given user.
    """
    expiration_hours = getattr(settings, 'JWT_EXPIRATION_HOURS', 24)
    
    payload = {
        'user_id': str(user.pk),
        'email': user.email,
        'exp': datetime.now(timezone.utc) + timedelta(hours=expiration_hours),
        'iat': datetime.now(timezone.utc),
        'type': 'access'
    }
    
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm='HS256'
    )
    
    return token


def generate_refresh_token(user):
    """
    Generate a refresh token for the given user.
    """
    import secrets
    from .models import RefreshToken
    
    token_value = secrets.token_urlsafe(64)
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    
    refresh_token = RefreshToken.objects.create(
        user=user,
        token=token_value,
        expires_at=expires_at
    )
    
    return refresh_token.token


def decode_token(token):
    """
    Decode a JWT token and return the payload.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=['HS256']
        )
        return payload
    except jwt.InvalidTokenError:
        return None
