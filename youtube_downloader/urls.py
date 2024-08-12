# youtube_downloader/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('download/<str:filename>/', views.download_audio, name='download_audio'),
]
