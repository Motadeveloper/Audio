import os
import random
import string
import yt_dlp
from django.shortcuts import render
from django.http import FileResponse, Http404
from django.conf import settings

def gerar_nome_aleatorio(extensao, tamanho=10):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(tamanho)) + '.' + extensao

def baixar_video(url, formato):
    ydl_opts = {
        'format': 'bestaudio/best' if formato == 'mp3' else 'bestvideo+bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio' if formato == 'mp3' else '',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if formato == 'mp3' else [],
        'ffmpeg_location': '/usr/bin/ffmpeg',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_title = info.get('title', 'video')
        video_filename = gerar_nome_aleatorio(formato)
        os.rename(f"{video_title}.{formato}", video_filename)

    return video_title, video_filename

def index(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        formato = request.POST.get('formato')
        video_title, video_filename = baixar_video(url, formato)

        return render(request, 'youtube_downloader/index.html', {
            'success': True,
            'video_title': video_title,
            'video_filename': video_filename,
            'formato': formato,
        })
    
    return render(request, 'youtube_downloader/index.html')

def download_audio(request, video_filename):
    file_path = os.path.join(settings.BASE_DIR, video_filename)
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), as_attachment=True)
        return response
    else:
        raise Http404("Arquivo não encontrado.")
