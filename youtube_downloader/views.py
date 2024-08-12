import os
import random
import string
import yt_dlp
from django.shortcuts import render, redirect
from django.http import FileResponse, Http404
from django.conf import settings

def gerar_nome_aleatorio(extensao, tamanho=10):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(tamanho)) + '.' + extensao

def baixar_video(url, formato, nome_arquivo):
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
        temp_filename = 'temp_video.' + (formato if formato == 'mp3' else 'mp4')
        
        # Gera o caminho final do arquivo com o nome fornecido pelo usuário
        final_file_path = os.path.join(settings.MEDIA_ROOT, nome_arquivo + '.' + formato)

        if os.path.exists(temp_filename):
            os.rename(temp_filename, final_file_path)
        else:
            raise FileNotFoundError(f"Arquivo {temp_filename} não encontrado.")

    return video_title, final_file_path

def index(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        formato = request.POST.get('formato')
        nome_arquivo = request.POST.get('nome_arquivo')
        try:
            video_title, final_file_path = baixar_video(url, formato, nome_arquivo)
            return render(request, 'youtube_downloader/index.html', {
                'video_title': video_title,
                'video_filename': os.path.basename(final_file_path),
            })
        except Exception as e:
            return render(request, 'index.html', {'error': str(e)})
    return render(request, 'youtube_downloader/index.html')

def download_audio(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    raise Http404("Arquivo não encontrado.")
