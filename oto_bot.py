import os
import json
from PIL import Image

# Klasör yollarını belirliyoruz
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
IMG_DIR = os.path.join(BASE_DIR, 'img', 'projeler')

# 1. Mevcut data.json dosyasını oku
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
else:
    data = {"profile": {}, "projects": []}

# Mevcut projelerin başlık ve açıklamaları silinmesin diye onları hafızaya alıyoruz
existing_projects = {p['id']: p for p in data.get('projects', [])}
updated_projects_list = []

# 2. img/projeler/ klasöründeki TÜM dosyaları tara
if os.path.exists(IMG_DIR):
    for folder_name in os.listdir(IMG_DIR):
        project_dir = os.path.join(IMG_DIR, folder_name)
        
        # Eğer bu bir klasörse ve içinde 'src' klasörü varsa, bu bir mimari projedir!
        if os.path.isdir(project_dir):
            src_dir = os.path.join(project_dir, 'src')
            if os.path.exists(src_dir):
                
                # Proje daha önce data.json'da yoksa (YENİ EKLENDİYSE)
                if folder_name not in existing_projects:
                    print(f"🌟 Yeni proje keşfedildi ve sisteme ekleniyor: {folder_name}")
                    # Klasör isminden otomatik bir başlık üret (örnek: paylasimli-ofis -> Paylasimli Ofis)
                    title_guess = folder_name.replace('-', ' ').replace('_', ' ').title()
                    
                    project_data = {
                        "id": folder_name,
                        "title": title_guess,
                        "year": "2026",
                        "summary": "Bu proje için henüz bir açıklama girilmedi.",
                        "previewImages": {},
                        "detailImages": []
                    }
                else:
                    project_data = existing_projects[folder_name]

                # --- RESİM İŞLEME VE THUMBNAIL ÜRETİMİ ---
                thumb_dir = os.path.join(project_dir, 'thumb')
                os.makedirs(thumb_dir, exist_ok=True)
                detail_images = []
                
                if 'previewImages' not in project_data:
                    project_data['previewImages'] = {}

                # Desteklenen resim formatları (Senin yüklediğin Webp dahil)
                valid_exts = ('.jpg', '.jpeg', '.png', '.webp')
                images = [f for f in os.listdir(src_dir) if f.lower().endswith(valid_exts)]
                images.sort() # Resimleri ismine göre sıraya diz

                for img_name in images:
                    src_path = os.path.join(src_dir, img_name)
                    thumb_path = os.path.join(thumb_dir, img_name)
                    img_lower = img_name.lower()

                    # Resmi aç, boyutlarını al ve düşük kaliteli (thumb) versiyonunu kaydet
                    with Image.open(src_path) as img:
                        width, height = img.size
                        if not os.path.exists(thumb_path):
                            # thumbnail fonksiyonu en boy oranını bozmadan resmi maksimum 800px'e küçültür
                            img.thumbnail((800, 800))
                            
                            # WebP resimlerini kaydederken uyumluluk sorunu olmaması için RGB'ye çeviriyoruz
                            if img.mode in ("RGBA", "P"):
                                img = img.convert("RGB")
                            
                            img.save(thumb_path, format="JPEG" if img_lower.endswith('.jpg') else None)
                    
                    # Sitenin okuyacağı bağlantı adreslerini oluştur
                    web_src = f"img/projeler/{folder_name}/src/{img_name}"
                    web_thumb = f"img/projeler/{folder_name}/thumb/{img_name}"
                    
                    # Alt metin (SEO) temizliği
                    clean_name = img_lower.replace('_kapak', '').replace('_yan1', '').replace('_yan2', '')
                    clean_name = os.path.splitext(clean_name)[0]
                    alt_text = clean_name.replace('_', ' ').replace('-', ' ').title()

                    detail_images.append({
                        "src": web_src,
                        "thumb": web_thumb,
                        "width": width,
                        "height": height,
                        "alt": alt_text
                    })

                    # Kapak ve yan görsel etiketleri kontrolü
                    if '_kapak' in img_lower:
                        project_data['previewImages']['kapak'] = web_thumb
                    elif '_yan1' in img_lower:
                        project_data['previewImages']['yan1'] = web_thumb
                    elif '_yan2' in img_lower:
                        project_data['previewImages']['yan2'] = web_thumb
                
                project_data['detailImages'] = detail_images
                updated_projects_list.append(project_data)

# 3. Güncellenmiş projeler listesini ana veriye ata
data['projects'] = updated_projects_list

# 4. JSON dosyasını kusursuz bir şekilde baştan yaz
with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Mükemmel! Klasörler tarandı, yeni projeler keşfedildi, thumb'lar üretildi ve data.json güncellendi.")