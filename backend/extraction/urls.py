from django.urls import path
from . import views

urlpatterns = [
    path('<uuid:pk>/', views.proposal_detail, name='proposal-detail'),
]
