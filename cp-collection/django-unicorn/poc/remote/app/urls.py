from django.urls import path, include

urlpatterns = [
    path("unicorn/", include("django_unicorn.urls")),
]
