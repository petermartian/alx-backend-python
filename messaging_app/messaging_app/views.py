from django.http import HttpResponse


def ping(_request):
    return HttpResponse("pong")
