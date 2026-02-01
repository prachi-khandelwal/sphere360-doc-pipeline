"""URL configuration."""
from django.urls import path, include

urlpatterns = [
    path('api/', include('documents.api.urls')),
]
