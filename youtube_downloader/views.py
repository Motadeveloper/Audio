from django.shortcuts import render
from django.http import HttpResponse
import yt_dlp
import uuid
from io import BytesIO

def baixar_audio_video(url, formato):
    nome_base = str(uuid.uuid4())  # Gera um nome de arquivo único
    buffer = BytesIO()  # Usar um buffer de memória

    ydl_opts = {
        'format': 'bestaudio/best' if formato == 'mp3' else 'bestvideo+bestaudio/best',
        'outtmpl': f'{nome_base}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if formato == 'mp3' else [],
        'outtmpl': '-',  # Saída como fluxo padrão
        'quiet': True,  # Suprimir a saída do yt-dlp
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        info_dict = ydl.extract_info(url, download=False)
        if formato == 'mp3':
            ydl.process_info(info_dict)
            buffer.write(ydl.download([url]))
        else:
            buffer.write(ydl.download([url]))

    buffer.seek(0)
    return buffer, f"{info_dict['title']}.{formato}"

def index(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        formato = request.POST.get('formato')

        buffer, filename = baixar_audio_video(url, formato)

        response = HttpResponse(buffer, content_type='audio/mpeg' if formato == 'mp3' else 'video/mp4')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response
    return render(request, 'youtube_downloader/index.html')
