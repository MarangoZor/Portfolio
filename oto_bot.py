import os
import json
import re
from PIL import Image

# Klasör yollarını belirliyoruz
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
IMG_DIR = os.path.join(BASE_DIR, 'img', 'projeler')

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
else:
    data = {"profile": {}, "projects": []}

existing_projects = {p['id']: p for p in data.get('projects', [])}
updated_projects_list = []

if os.path.exists(IMG_DIR):
    for folder_name in os.listdir(IMG_DIR):
        project_dir = os.path.join(IMG_DIR, folder_name)
        
        if os.path.isdir(project_dir):
            src_dir = os.path.join(project_dir, 'src')
            if os.path.exists(src_dir):
                
                if folder_name not in existing_projects:
                    print(f"🌟 Yeni proje keşfedildi ve sisteme ekleniyor: {folder_name}")
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

                thumb_dir = os.path.join(project_dir, 'thumb')
                os.makedirs(thumb_dir, exist_ok=True)
                detail_images = []
                
                if 'previewImages' not in project_data:
                    project_data['previewImages'] = {}

                valid_exts = ('.jpg', '.jpeg', '.png', '.webp')
                images = [f for f in os.listdir(src_dir) if f.lower().endswith(valid_exts)]
                images.sort()

                for img_name in images:
                    src_path = os.path.join(src_dir, img_name)
                    thumb_path = os.path.join(thumb_dir, img_name)
                    img_lower = img_name.lower()

                    with Image.open(src_path) as img:
                        width, height = img.size
                        if not os.path.exists(thumb_path):
                            img.thumbnail((800, 800))
                            if img.mode in ("RGBA", "P"):
                                img = img.convert("RGB")
                            img.save(thumb_path, format="JPEG" if img_lower.endswith('.jpg') else None)
                    
                    web_src = f"img/projeler/{folder_name}/src/{img_name}"
                    web_thumb = f"img/projeler/{folder_name}/thumb/{img_name}"
                    
                    # YENİ ZEKA: Dosya isminden açıklamayı otomatik çıkarma (Zemin-Kat-Planı -> Zemin Kat Planı)
                    base_name = os.path.splitext(img_name)[0]
                    clean_name = re.sub(r'(?i)_kapak|_yan1|_yan2', '', base_name) # Kapak vb. yazıları sil
                    parts = clean_name.split('_') # İsimleri "_" işaretine göre böl
                    
                    alt_text = ""
                    # Eğer ismin son parçasında metin varsa (rakam değilse), onu açıklama olarak al
                    if len(parts) > 1:
                        last_part = parts[-1]
                        if not last_part.isdigit() and len(last_part) > 1:
                            alt_text = last_part.replace('-', ' ') # Tireleri boşluk yap

                    detail_images.append({
                        "src": web_src,
                        "thumb": web_thumb,
                        "width": width,
                        "height": height,
                        "alt": alt_text # Eğer metin yoksa JSON'a "" (boşluk) olarak kaydedilir
                    })

                    if '_kapak' in img_lower:
                        project_data['previewImages']['kapak'] = web_thumb
                    elif '_yan1' in img_lower:
                        project_data['previewImages']['yan1'] = web_thumb
                    elif '_yan2' in img_lower:
                        project_data['previewImages']['yan2'] = web_thumb
                
                project_data['detailImages'] = detail_images
                updated_projects_list.append(project_data)

data['projects'] = updated_projects_list

with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Mükemmel! İsimlerden açıklamalar okundu, klasörler tarandı ve data.json güncellendi.")