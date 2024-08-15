from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
import yt_dlp
import uuid
import os
from io import BytesIO
from .models import VideoInfo

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

def get_video_info(request):
    url = request.GET.get('url')
    video_info = obter_informacoes_video(url)
    
    # Salvar ou atualizar as informações do vídeo no banco de dados
    video, created = VideoInfo.objects.get_or_create(
        url=url,
        defaults={
            'title': video_info['titulo'],
            'thumbnail_url': video_info['thumbnail'],
        }
    )
    
    if not created:
        video.request_count += 1
        video.save()

    return JsonResponse(video_info)

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
    ext = 'mp3' if formato == 'mp3' else info_dict['ext']
    filename = f"{info_dict['title']}.{ext}"
    full_temp_filepath = temp_filepath.replace('%(ext)s', ext)

    # Ler o arquivo temporário no buffer de memória
    with open(full_temp_filepath, 'rb') as f:
        buffer = BytesIO(f.read())

    # Apagar o arquivo temporário após o uso
    os.remove(full_temp_filepath)

    buffer.seek(0)
    return buffer, filename

def download_video(request):
    url = request.GET.get('url')
    formato = request.GET.get('format')

    buffer, filename = baixar_audio_video(url, formato)

    response = HttpResponse(buffer, content_type='audio/mpeg' if formato == 'mp3' else 'video/mp4')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response

def video_info_list(request):
    page_number = request.GET.get('page', 1)
    videos = VideoInfo.objects.all().order_by('-request_count')
    paginator = Paginator(videos, 5)  # 5 vídeos por página
    page_obj = paginator.get_page(page_number)

    total_conversions = VideoInfo.total_conversions()

    video_data = []
    for video in page_obj:
        video_id = video.url.split('=')[-1]  # Extrair o ID do vídeo
        video_data.append({
            'title': video.title,
            'url': video.url,
            'video_id': video_id,  # Passa o ID do vídeo
            'thumbnail_url': video.thumbnail_url,
            'request_count': video.request_count,
        })

    # Verificação se a requisição é AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(video_data, safe=False)

    return render(request, 'youtube_downloader/video_info_list.html', {
        'video_data': video_data,
        'total_conversions': total_conversions,
    })

def index(request):
    return render(request, 'youtube_downloader/index.html')
