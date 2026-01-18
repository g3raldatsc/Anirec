import requests
import pandas as pd
import time

OUTPUT_FILE = 'dataset_anime_romance.csv'

def get_romance_genre_id():
    """Mencari ID genre Romance"""
    url = "https://api.jikan.moe/v4/genres/anime"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            genres = response.json()['data']
            for genre in genres:
                if genre['name'] == 'Romance':
                    return genre['mal_id']
    except Exception as e:
        print(f"Gagal koneksi awal: {e}")
    return None

def fetch_all_romance_anime():
    genre_id = get_romance_genre_id()
    if not genre_id:
        print("Gagal menemukan ID genre Romance.")
        return []

    print(f"ID Genre Romance ditemukan: {genre_id}")
    anime_data = []
    
    page = 1
    has_next_page = True
    
    # Loop
    while has_next_page:
        url = f"https://api.jikan.moe/v4/anime?genres={genre_id}&page={page}&order_by=popularity&sort=asc"
        
        # Retry
        max_retries = 3
        success = False
        
        for attempt in range(max_retries):
            try:
                print(f"Mengambil halaman {page}... (Total data didapat: {len(anime_data)})")
                response = requests.get(url, timeout=10) # Timeout (10)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data['data']
                    
                    for item in items:
                        genre_list = [g['name'] for g in item['genres']]
                        genres_str = ", ".join(genre_list)
                        
                        poster_url = item['images']['jpg']['large_image_url']
                        if not poster_url:
                            poster_url = item['images']['jpg']['image_url']

                        sinopsis_bersih = item['synopsis'] if item['synopsis'] else ""

                        entry = {
                            'mal_id': item['mal_id'],
                            'title': item['title'],
                            'score': item['score'],
                            'genres': genres_str,
                            'synopsis': sinopsis_bersih,
                            'image_url': poster_url,
                            'type': item['type'],
                            'episodes': item['episodes'],
                            'members': item['members'],
                            'url': item['url']
                        }
                        anime_data.append(entry)
                    
                    has_next_page = data['pagination']['has_next_page']
                    success = True
                    break 
                
                elif response.status_code == 429:
                    print(f"  Rate Limit! Menunggu {5 * (attempt + 1)} detik...")
                    time.sleep(5 * (attempt + 1)) 
                
                else:
                    print(f"  Gagal status {response.status_code}. Mencoba ulang...")
                    time.sleep(2)
            
            except Exception as e:
                print(f"  Error koneksi: {e}. Mencoba ulang...")
                time.sleep(2)
        
        if not success:
            print(f"Gagal total mengambil halaman {page}. Melompati halaman ini.")
            if not has_next_page:
                break

        page += 1
        time.sleep(1.5) 

    return anime_data

if __name__ == "__main__":
    print("Mulai scaping data anime genre Romance dari Jikan API...")
    print("Mohon bersabar, ini akan memakan waktu...")
    
    results = fetch_all_romance_anime()
    
    if results:
        df = pd.DataFrame(results)
        df.to_csv(OUTPUT_FILE, index=False)
        
        print(f"\n" + "="*40)
        print(f"Selesai! Total {len(df)} data anime berhasil diambil.")
        print(f"Data tersimpan di: {OUTPUT_FILE}")
        print("="*40)
    else:
        print("Gagal mengambil data.")