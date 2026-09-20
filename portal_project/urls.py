# ==========================================
# PROJECT JHEP NGO PORTAL - ROOT URL CONFIGURATION
# ==========================================

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Built-In Admin Site
    path('django-admin/', admin.site.urls),

    # Project Jhep NGO Portal Application Routes
    path('', include('portal.urls')),
]
