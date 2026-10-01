from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def inicio(request):
    return render(request, "portal/inicio.html")


@require_GET
def salud(request):
    """Comprobación mínima para despliegues y monitoreo."""
    return JsonResponse({"estado": "disponible"})
