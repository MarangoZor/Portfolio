import os
import json
from PIL import Image

# Klasör yollarını belirliyoruz
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
IMG_DIR = os.path.join(BASE_DIR, 'img', 'projeler')

# Mevcut data.json dosyasını okuyoruz
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# JSON içindeki projeleri tek tek geziyoruz
for project in data.get('projects', []):
    pid = project['id']
    project_dir = os.path.join(IMG_DIR, pid)
    src_dir = os.path.join(project_dir, 'src')
    thumb_dir = os.path.join(project_dir, 'thumb')

    # Eğer projenin 'src' (yüksek çözünürlük) klasörü varsa işlemleri başlat
    if os.path.exists(src_dir):
        os.makedirs(thumb_dir, exist_ok=True) # thumb klasörü yoksa yarat
        detail_images = []

        # Eğer data.json içinde previewImages objesi yoksa hata vermemesi için oluştur
        if 'previewImages' not in project:
            project['previewImages'] = {}

        # Sadece resim dosyalarını al ve isme göre (001, 002...) sırala
        valid_exts = ('.jpg', '.jpeg', '.png', '.webp')
        images = [f for f in os.listdir(src_dir) if f.lower().endswith(valid_exts)]
        images.sort()

        for img_name in images:
            src_path = os.path.join(src_dir, img_name)
            thumb_path = os.path.join(thumb_dir, img_name)
            img_lower = img_name.lower()

            # Resmi açıp genişlik ve yüksekliğini alıyoruz
            with Image.open(src_path) as img:
                width, height = img.size
                
                # Eğer resmin düşük boyutlu (thumb) hali henüz üretilmemişse üret!
                if not os.path.exists(thumb_path):
                    # Orijinal oranı bozmadan maksimum 800px olacak şekilde küçült
                    img.thumbnail((800, 800))
                    img.save(thumb_path)
            
            # Web sitesi için linkleri oluştur
            web_src = f"img/projeler/{pid}/src/{img_name}"
            web_thumb = f"img/projeler/{pid}/thumb/{img_name}"
            
            # Alt metni temizle (03_kapak.jpg -> 03 olarak temizlenir, arkada pis kod kalmaz)
            clean_name = img_lower.replace('_kapak', '').replace('_yan1', '').replace('_yan2', '')
            clean_name = os.path.splitext(clean_name)[0]
            alt_text = clean_name.replace('_', ' ').replace('-', ' ').title()

            # Proje detay sayfasına (Masonry galeriye) tüm resimleri sırasıyla ekle
            detail_images.append({
                "src": web_src,
                "thumb": web_thumb,
                "width": width,
                "height": height,
                "alt": alt_text
            })

            # SENİN FİKRİN: İsimde özel etiket varsa, ana sayfadaki kapak resimlerine (thumb formatında) ata!
            if '_kapak' in img_lower:
                project['previewImages']['kapak'] = web_thumb
            elif '_yan1' in img_lower:
                project['previewImages']['yan1'] = web_thumb
            elif '_yan2' in img_lower:
                project['previewImages']['yan2'] = web_thumb
        
        # Projenin detay resimlerini json'da güncelle
        project['detailImages'] = detail_images

# Tüm işlemler bitince JSON dosyasını baştan yazarak kaydet
with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Mükemmel! Resimler okundu, thumb'lar üretildi, kapak fotoğrafları seçildi ve data.json hatasız güncellendi.")