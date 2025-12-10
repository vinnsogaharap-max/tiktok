from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import time

app = Flask(__name__)

# Fungsi untuk mendownload video
def download_video(url, type_download):
    timestamp = int(time.time())
    
    # Opsi yt-dlp
    ydl_opts = {
        'outtmpl': f'downloads/tiktok_{timestamp}.%(ext)s', # Nama file sementara
        'quiet': True,
        'no_warnings': True,
    }

    # Logika Pilihan Resolusi/Tipe
    # TikTok jarang punya banyak resolusi (misal 360p, 720p terpisah).
    # Biasanya hanya ada "Source" (Kualitas Terbaik).
    if type_download == 'audio':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    else:
        # Format 'best' di yt-dlp untuk TikTok biasanya otomatis No Watermark
        # jika tersedia dari source-nya.
        ydl_opts['format'] = 'best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Jika convert ke mp3, nama file berubah
            if type_download == 'audio':
                filename = filename.rsplit('.', 1)[0] + '.mp3'
                
            return filename, info.get('title', 'video')
    except Exception as e:
        print(f"Error: {e}")
        return None, None

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form.get('url')
        pilihan = request.form.get('pilihan') # video atau audio
        
        if url:
            # Proses Download di Server (Termux)
            file_path, title = download_video(url, pilihan)
            
            if file_path and os.path.exists(file_path):
                # Kirim file ke User (Browser)
                # as_attachment=True membuat browser otomatis memunculkan pop-up download
                try:
                    return send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path))
                finally:
                    # OPSI: Hapus file di Termux setelah dikirim agar memori aman
                    # Kami beri delay sedikit atau biarkan OS menghandle, 
                    # tapi untuk simpel kita biarkan dulu di folder downloads
                    pass
            else:
                return "Gagal mengambil video. Pastikan link benar."
    
    return render_template('index.html')

if __name__ == '__main__':
    # Buat folder downloads jika belum ada
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        
    # Jalankan server di port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
