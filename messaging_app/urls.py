from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect
from django.http import HttpResponse


def health(_request):
    return HttpResponse("ok")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", lambda r: redirect("/api/", permanent=False)),
    path("health/", health, name="health"),
    path("api/", include("chats.urls")),
]
