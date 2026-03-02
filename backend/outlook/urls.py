from django.urls import path
from . import views

urlpatterns = [
    path('vendors/', views.outlook_vendors, name='outlook-vendors'),
    path('clients/', views.outlook_clients, name='outlook-clients'),
    path('fetch/', views.outlook_fetch, name='outlook-fetch'),
]
