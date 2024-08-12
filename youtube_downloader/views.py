import os
import yt_dlp
from django.shortcuts import render
from django.http import FileResponse, Http404
from django.conf import settings

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
        video_title = info.get('title', None)
        video_filename = f"{video_title.replace(' ', '_').lower()}.{formato}"
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
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{video_filename}"'
        os.remove(file_path)
        return response
    else:
        raise Http404("Arquivo não encontrado.")
