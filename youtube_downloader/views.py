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
        'outtmpl': 'temp_video.%(ext)s',  # Nome temporário
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_title = info.get('title', 'video')
        temp_filename = 'temp_video.' + formato

        video_filename = gerar_nome_aleatorio(formato)
        temp_file_path = os.path.join(settings.BASE_DIR, temp_filename)
        final_file_path = os.path.join(settings.BASE_DIR, video_filename)

        if os.path.exists(temp_file_path):
            os.rename(temp_file_path, final_file_path)
        else:
            raise FileNotFoundError(f"Arquivo {temp_file_path} não encontrado.")

    return video_title, video_filename

def index(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        formato = request.POST.get('formato')
        try:
            video_title, video_filename = baixar_video(url, formato)
            return render(request, 'youtube_downloader/index.html', {
                'success': True,
                'video_title': video_title,
                'video_filename': video_filename,
                'formato': formato,
            })
        except FileNotFoundError as e:
            return render(request, 'youtube_downloader/index.html', {
                'error': str(e),
            })
    
    return render(request, 'youtube_downloader/index.html')
