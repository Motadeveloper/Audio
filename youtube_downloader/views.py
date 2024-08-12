from django.shortcuts import render
import yt_dlp
import uuid
import os
from django.conf import settings

def baixar_audio_video(url):
    nome_base = str(uuid.uuid4())  # Gera um nome de arquivo único

    # Configuração para baixar o áudio (MP3)
    audio_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(settings.MEDIA_ROOT, f'{nome_base}.mp3'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    # Configuração para baixar o vídeo (MP4)
    video_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(settings.MEDIA_ROOT, f'{nome_base}.mp4'),
    }

    with yt_dlp.YoutubeDL(audio_opts) as ydl_audio, yt_dlp.YoutubeDL(video_opts) as ydl_video:
        info = ydl_audio.extract_info(url, download=True)
        ydl_video.download([url])

        return {
            'titulo': info.get('title', 'Título Desconhecido'),
            'thumbnail': info.get('thumbnail', ''),
            'audio_quality': '320kbps',
            'video_quality': info.get('format', 'Desconhecido').split(' ')[-1],
            'nome_mp3': f'{nome_base}.mp3',
            'nome_mp4': f'{nome_base}.mp4',
        }

def index(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        video_info = baixar_audio_video(url)
        return render(request, 'youtube_downloader/index.html', {
            'success': True,
            'titulo_video': video_info['titulo'],
            'thumbnail': video_info['thumbnail'],
            'audio_quality': video_info['audio_quality'],
            'video_quality': video_info['video_quality'],
            'nome_mp3': video_info['nome_mp3'],
            'nome_mp4': video_info['nome_mp4'],
        })
    return render(request, 'youtube_downloader/index.html')
