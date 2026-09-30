import requests
import json
from datetime import date

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "PersijaTV"
MAX_RESULT = 50

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

def get_video_ids(playlistId):
    # Inisialisasi list kosong untuk menampung seluruh ID video yang ditemukan
    video_ids = []
    # Token penanda halaman berikutnya (diinisialisasi None untuk halaman pertama)
    pageToken = None

    # Menyusun URL dasar endpoint playlistItems YouTube Data API v3
    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={MAX_RESULT}&playlistId={playlistId}&key={API_KEY}"

    try:
        # Perulangan untuk mengambil data terus-menerus selama halaman berikutnya masih ada
        while True:
            # Mengatur URL request awal dari URL dasar
            url = base_url

            # Jika ada pageToken (halaman berikutnya), tambahkan parameter pageToken ke URL
            if pageToken:
                url += f"&pageToken={pageToken}"

            # Mengirimkan permintaan HTTP GET ke YouTube API
            response = requests.get(url)

            # Memastikan request berhasil (melempar HTTPError jika kode status respon adalah 4xx atau 5xx)
            response.raise_for_status()

            # Mengubah hasil respon JSON menjadi dictionary Python
            data = response.json()

            # Melakukan perulangan untuk setiap item video yang ada di dalam list 'items'
            for item in data.get('items', []):
                # Mengambil ID video dari contentDetails item tersebut
                video_id = item['contentDetails']['videoId']
                # Memasukkan ID video ke dalam list video_ids
                video_ids.append(video_id)

            # Mengambil token halaman berikutnya dari respon (bernilai None jika sudah di halaman terakhir)
            pageToken = data.get('nextPageToken')

            # Jika tidak ada halaman berikutnya lagi, hentikan perulangan while
            if not pageToken:
                break

        # Mengembalikan list lengkap berisi seluruh ID video yang terkumpul
        return video_ids

    # Menangkap error jika terjadi kegagalan saat request HTTP
    except requests.exceptions.RequestException as e:
        # Melempar kembali error tersebut ke pemanggil fungsi
        raise e


def extract_video_data(video_ids):
    extracted_data = []

    def batch_list(video_id_lst, batch_size):
        for video_id in range(0, len(video_id_lst), batch_size):
            yield video_id_lst[video_id:video_id + batch_size]

    try:
        for batch in batch_list(video_ids, MAX_RESULT):
            video_ids_str = ",".join(batch)

            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}"

            response = requests.get(url)
            response.raise_for_status()

            data = response.json()

            for item in data.get("items", []):
                video_id = item["id"]
                stats = item["statistics"]
                snippet = item["snippet"]
                contentDetails = item['contentDetails']

                # Menyusun dictionary yang berisi informasi video
                video_data = {
                    "video_id": video_id,
                    "title": snippet.get("title"),
                    "channel_id": snippet.get("channelId"),
                    "channel_title": snippet.get("channelTitle"),
                    "duration": contentDetails['duration'],
                    "published_at": snippet.get("publishedAt"),
                    "view_count": stats.get("viewCount", None),
                    "like_count": stats.get("likeCount", None),
                    "comment_count": stats.get("commentCount", None)
                }
                # Menambahkan dictionary video_data ke dalam list extracted_data
                extracted_data.append(video_data)
        
        # Mengembalikan list lengkap berisi seluruh dictionary video yang terkumpul
        return extracted_data

    except requests.exceptions.RequestException as e:
        # Melempar kembali error tersebut ke pemanggil fungsi
        raise e

def save_to_json(extract_data):
    # Menyimpan data ke dalam file JSON
    file_path = f"./data/YT_data_{date.today()}.json"

    # Membuka file JSON dalam mode tulis ('w') dengan encoding UTF-8
    # 'with open(...)' memastikan file tertutup secara otomatis setelah blok kode selesai
    with open(file_path, 'w', encoding='utf-8') as json_file:
        # Menggunakan json.dump() untuk menuliskan data ke dalam file
        # indent=4 digunakan agar format JSON menjadi rapi dan mudah dibaca (human-readable)
        # ensure_ascii=False digunakan agar karakter non-ASCII dapat tersimpan dengan benar
        json.dump(extract_data, json_file, indent=4, ensure_ascii=False)

# Mengecek apakah script ini dijalankan secara langsung (sebagai program utama)
if __name__ == '__main__':
    
    # Memanggil fungsi get_playlist_id untuk dieksekusi
    playlistId = get_playlist_id()
    
    # Menggunakan function get_video_ids untuk mendapatkan ID video
    video_ids = get_video_ids(playlistId)

    # Menggunakan function extract_video_data untuk mengekstrak data video
    video_data = extract_video_data(video_ids)

    # Menggunakan function save_to_json untuk menyimpan data video
    save_to_json(video_data)
    
# Dijalankan jika file ini diimpor sebagai modul oleh file Python lain
else:
    # Menampilkan pesan bahwa file ini dirancang untuk dijalankan sebagai script mandiri
    print("This script should be run as a standalone script.")