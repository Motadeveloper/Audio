from django.shortcuts import render
import yt_dlp
import os
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
        ydl.download([url])
    print(f"Áudio salvo como {nome_arquivo}.mp3")

def index(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        nome_arquivo = str(uuid.uuid4())  # Gera um nome de arquivo único
        baixar_audio(url, nome_arquivo)
        return render(request, 'youtube_downloader/index.html', {'success': True, 'nome_arquivo': nome_arquivo})
    return render(request, 'youtube_downloader/index.html')
