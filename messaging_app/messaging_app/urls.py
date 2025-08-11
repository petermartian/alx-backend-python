from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from chats.views import ConversationViewSet, MessageViewSet

def root(request):
    return JsonResponse({"status": "ok", "message": "Messaging API up"})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return JsonResponse({"message": f"Hello {request.user.username}, you are authenticated!"})

router = DefaultRouter()
router.register(r"conversations", ConversationViewSet, basename="conversation")
router.register(r"messages", MessageViewSet, basename="message")

urlpatterns = [
    path("", root, name="root"),
    path("protected/", protected_view, name="protected"),
    path("admin/", admin.site.urls),

    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("api/", include(router.urls)),
]
