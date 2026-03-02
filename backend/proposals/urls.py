from django.urls import path
from . import views

urlpatterns = [
    path('<uuid:pk>/generate/', views.generate_proposal, name='generate-proposal'),
    path('<uuid:pk>/download/', views.download_proposal, name='download-proposal'),
]
