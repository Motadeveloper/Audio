import os
import yt_dlp
from django.shortcuts import render
from django.http import FileResponse, Http404
from django.conf import settings

def baixar_audio(url, nome_arquivo):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{nome_arquivo}.mp3',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_title = info.get('title', None)
        video_duration = info.get('duration', None)
        video_thumbnail = info.get('thumbnail', None)

    return video_title, video_duration, video_thumbnail

def index(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        nome_arquivo = request.POST.get('nome_arquivo')
        video_title, video_duration, video_thumbnail = baixar_audio(url, nome_arquivo)

        return render(request, 'youtube_downloader/index.html', {
            'success': True,
            'nome_arquivo': nome_arquivo,
            'video_title': video_title,
            'video_duration': video_duration,
            'video_thumbnail': video_thumbnail,
        })
    
    return render(request, 'youtube_downloader/index.html')

def download_audio(request, nome_arquivo):
    file_path = os.path.join(settings.BASE_DIR, f'{nome_arquivo}.mp3')
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}.mp3"'
        os.remove(file_path)
        return response
    else:
        raise Http404
