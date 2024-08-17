from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_video_info/', views.get_video_info, name='get_video_info'),
    path('download_video/', views.download_video, name='download_video'),
    path('info/', views.video_info_list, name='video_info_list'),  # Nova rota para a lista de vídeos
    path('playlist/', views.playlist_converter, name='playlist_converter'),
]
