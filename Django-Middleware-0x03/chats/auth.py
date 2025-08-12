from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomJWTAuthentication(JWTAuthentication):
    """
    Thin wrapper so settings can reference a stable app path if needed.
    """
    pass
