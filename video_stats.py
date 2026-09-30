import requests
import json

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "PersijaTV"

# Mendefinisikan fungsi untuk mengambil ID playlist unggahan (uploads) dari channel YouTube
def get_playlist_id():

    try:
        # Menyusun URL endpoint YouTube Data API v3 untuk mengambil contentDetails channel berdasarkan handle
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"

        # Mengirimkan permintaan HTTP GET ke endpoint YouTube API
        response = requests.get(url)

        # Memastikan request berhasil (melempar HTTPError jika kode status respon adalah 4xx atau 5xx)
        response.raise_for_status()

        # Mengurai (parse) respon yang diterima dari format JSON menjadi dictionary Python
        data = response.json()

        # Mengambil data channel pertama dari array 'items'
        channel_items = data['items'][0]
        # Mengambil ID playlist 'uploads' (daftar semua video yang diunggah channel tersebut)
        channel_playlistId = channel_items['contentDetails']['relatedPlaylists']['uploads']

        print(channel_playlistId)
        # Mengembalikan nilai ID playlist yang didapatkan
        return channel_playlistId

    # Menangkap pengecualian (exception) jika terjadi masalah jaringan atau error saat request
    except requests.exceptions.RequestException as e:
        # Melempar kembali error tersebut ke pemanggil fungsi
        raise e

# Mengecek apakah script ini dijalankan secara langsung (sebagai program utama)
if __name__ == '__main__':
    # Menampilkan pesan ke terminal bahwa proses pengambilan ID playlist sedang berjalan
    print("Getting channel playlist ID...")
    # Memanggil fungsi get_playlist_id untuk dieksekusi
    get_playlist_id()
# Dijalankan jika file ini diimpor sebagai modul oleh file Python lain
else:
    # Menampilkan pesan bahwa file ini dirancang untuk dijalankan sebagai script mandiri
    print("This script should be run as a standalone script.")