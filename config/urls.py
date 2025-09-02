from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    
    path("leaves/", include("leaves.urls")), # 👈 add this line
    path("", RedirectView.as_view(pattern_name="leaves:list", permanent=False)),
]
