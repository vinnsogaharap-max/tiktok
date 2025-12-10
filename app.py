import os
import tempfile
from flask import Flask, render_template, request, send_file, after_this_request
import yt_dlp

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    # Pastikan 'link' ini sesuai dengan name="..." di input HTML kamu
    # Kalau di HTML name="url", ganti ['link'] jadi ['url']
    url = request.form['url'] 
    
    # 1. Ambil lokasi folder sementara (/tmp) yang diizinkan Vercel
    temp_dir = tempfile.gettempdir()
    
    ydl_opts = {
        # Simpan file ke folder /tmp
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'format': 'mp4/best',
        'noplaylist': True,
    }

    try:
        # Proses Download dari TikTok ke Server Vercel
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # 2. Fungsi Hapus Otomatis (Supaya server gak penuh)
        @after_this_request
        def remove_file(response):
            try:
                os.remove(file_path)
                print(f"Berhasil menghapus file sementara: {file_path}")
            except Exception as e:
                print(f"Gagal menghapus file: {e}")
            return response

        # 3. Kirim file dari folder /tmp ke HP User
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return f"Terjadi kesalahan: {str(e)}"

# Ini cuma jalan kalau di laptop/termux lokal, di Vercel ini diabaikan
if __name__ == '__main__':
    app.run(debug=True)
