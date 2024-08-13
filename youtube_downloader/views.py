from django.shortcuts import render
from django.http import HttpResponse
import yt_dlp
import uuid
import os
from io import BytesIO

def obter_informacoes_video(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,  # Suprimir a saída do yt-dlp
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        return {
            'titulo': info_dict.get('title', 'Título Desconhecido'),
            'thumbnail': info_dict.get('thumbnail', ''),
            'extensoes': info_dict.get('ext', ''),
            'formato_audio': '320kbps',
            'formato_video': info_dict.get('format', 'Desconhecido').split(' ')[-1],
            'url': url,
        }

def baixar_audio_video(url, formato):
    nome_base = str(uuid.uuid4())  # Gera um nome de arquivo único
    temp_filepath = f'{nome_base}.%(ext)s'  # Arquivo temporário

    ydl_opts = {
        'format': 'bestaudio/best' if formato == 'mp3' else 'bestvideo+bestaudio/best',
        'outtmpl': temp_filepath,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if formato == 'mp3' else [],
        'quiet': True,  # Suprimir a saída do yt-dlp
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        info_dict = ydl.extract_info(url, download=False)

    # Identificar o nome completo do arquivo gerado
    filename = f"{info_dict['title']}.{formato}"
    full_temp_filepath = temp_filepath.replace('%(ext)s', formato)

    # Ler o arquivo temporário no buffer de memória
    with open(full_temp_filepath, 'rb') as f:
        buffer = BytesIO(f.read())

    # Apagar o arquivo temporário após o uso
    os.remove(full_temp_filepath)

    buffer.seek(0)
    return buffer, filename

def index(request):
    if request.method == 'POST':
        if 'url' in request.POST:
            url = request.POST.get('url')
            video_info = obter_informacoes_video(url)
            return render(request, 'youtube_downloader/index.html', {
                'video_info': video_info
            })
        elif 'formato' in request.POST:
            url = request.POST.get('url')
            formato = request.POST.get('formato')

            buffer, filename = baixar_audio_video(url, formato)

            response = HttpResponse(buffer, content_type='audio/mpeg' if formato == 'mp3' else 'video/mp4')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            return response
    return render(request, 'youtube_downloader/index.html')
