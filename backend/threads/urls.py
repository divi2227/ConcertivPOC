from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_thread, name='upload-thread'),
    path('', views.list_threads, name='list-threads'),
    path('<uuid:pk>/', views.thread_detail, name='thread-detail'),
    path('<uuid:pk>/analyze/', views.analyze_thread, name='analyze-thread'),
]
