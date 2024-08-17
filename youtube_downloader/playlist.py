import os
import yt_dlp as youtube_dl

def download_and_convert_playlist_to_mp3(playlist_url, download_path='downloads'):
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])

    print('Conversão concluída.')

if __name__ == "__main__":
    playlist_url = input("Digite a URL da playlist do YouTube: ")
    download_and_convert_playlist_to_mp3(playlist_url)
