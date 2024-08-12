from django.shortcuts import render
import yt_dlp
import uuid

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
        return {
            'titulo': info.get('title', 'Título Desconhecido'),
            'thumbnail': info.get('thumbnail', ''),
            'audio_quality': '320kbps',
            'video_quality': info.get('format', 'Desconhecido').split(' ')[-1]
        }

def index(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        nome_arquivo = str(uuid.uuid4())  # Gera um nome de arquivo único
        video_info = baixar_audio(url, nome_arquivo)
        return render(request, 'youtube_downloader/index.html', {
            'success': True,
            'nome_arquivo': nome_arquivo,
            'titulo_video': video_info['titulo'],
            'thumbnail': video_info['thumbnail'],
            'audio_quality': video_info['audio_quality'],
            'video_quality': video_info['video_quality']
        })
    return render(request, 'youtube_downloader/index.html')
