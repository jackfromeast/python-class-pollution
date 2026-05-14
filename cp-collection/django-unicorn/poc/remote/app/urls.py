from django.urls import path, include
from django.shortcuts import render
from django.http import JsonResponse
from django.core.signing import Signer, BadSignature


def home(request):
    return render(request, "home.html")


def admin_dashboard(request):
    token = request.GET.get("token", "")
    try:
        signer = Signer()
        value = signer.unsign(token)
        if value != "admin":
            raise BadSignature("not admin")
    except BadSignature:
        return JsonResponse({"error": "Invalid or expired admin token"}, status=403)
    return JsonResponse({
        "user": "admin",
        "role": "superuser",
        "email": "admin@novamart.io",
        "revenue": "$142,587",
        "orders_today": 47,
        "active_users": 1283,
    })


urlpatterns = [
    path("", home, name="home"),
    path("unicorn/", include("django_unicorn.urls")),
    path("api/admin/dashboard/", admin_dashboard, name="admin_dashboard"),
]
