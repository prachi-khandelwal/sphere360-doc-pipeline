"""API URL configuration."""
from django.urls import path
from .views import process_documents

urlpatterns = [
    path('process/', process_documents, name='process-documents')
   
]
