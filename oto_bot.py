import os
import json
import re
import fitz  # PyMuPDF kütüphanesi
import io
from PIL import Image
import gc  # RAM temizliği için

# --- GÜVENLİK VE LİMİT AYARLARI ---
Image.MAX_IMAGE_PIXELS = None 

# --- KULLANICI ETKİLEŞİMİ VE KALİTE SEÇİMİ ---
print("\n" + "="*50)
print("🚀 MİMARİ PORTFOLYO OTO-BOT BAŞLATILIYOR")
print("="*50)
print("Kalite Seçimi (1-10):")
print("10: Ultra Net (4x - Çok Yavaş)")
print("8 : Standart Yüksek (2x - Önerilen)")
print("7 : Orijinal Boyut (1x - Dengeli)")
print("5 : Hızlı Taslak (0.6x - Küçük Dosya)")
print("1 : En Düşük (0.2x - Çok Hızlı)")
print("="*50)

try:
    user_input = int(input("Lütfen bir kalite değeri girin (1-10): "))
    if not (1 <= user_input <= 10):
        raise ValueError
except ValueError:
    print("⚠️ Geçersiz giriş! Varsayılan değer (8) seçildi.")
    user_input = 8

# Giriş değerini ölçeğe çevirme (Map)
quality_map = {
    10: 4.0, 9: 3.0, 8: 2.0, 7: 1.0, 
    6: 0.8, 5: 0.6, 4: 0.5, 3: 0.4, 2: 0.3, 1: 0.2
}
SCALE_FACTOR = quality_map.get(user_input, 2.0)
print(f"⚙️ Çözünürlük Çarpanı: {SCALE_FACTOR}x olarak ayarlandı.\n")

# --- KLASÖR YOLLARI ---
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

def get_sort_key(folder_name):
    parts = folder_name.split('_', 1)
    if len(parts) == 2 and parts[0].isdigit():
        return (int(parts[0]), parts[1].lower())
    return (float('inf'), folder_name.lower())

if os.path.exists(IMG_DIR):
    folders = [f for f in os.listdir(IMG_DIR) if os.path.isdir(os.path.join(IMG_DIR, f))]
    folders.sort(key=get_sort_key)
    
    for folder_name in folders:
        project_dir = os.path.join(IMG_DIR, folder_name)
        src_dir = os.path.join(project_dir, 'src')
        
        # PDF Kontrolü
        pdf_files = [f for f in os.listdir(project_dir) if f.lower().endswith('.pdf')]
        
        if pdf_files:
            os.makedirs(src_dir, exist_ok=True)
            pdf_files.sort()
            existing_src_files = os.listdir(src_dir)
            kapak_assigned = any("_kapak" in f.lower() for f in existing_src_files)
            
            for pdf_file in pdf_files:
                pdf_path = os.path.join(project_dir, pdf_file)
                pdf_base_name = os.path.splitext(pdf_file)[0]
                already_processed = any(f.startswith(pdf_base_name + "_01") for f in existing_src_files)
                
                if not already_processed:
                    print(f"📄 İşleniyor ({user_input}/10 kalite): {pdf_file}")
                    doc = fitz.open(pdf_path)
                    
                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        # Seçilen kaliteye göre matris oluşturma
                        mat = fitz.Matrix(SCALE_FACTOR, SCALE_FACTOR)
                        pix = page.get_pixmap(matrix=mat)
                        
                        img_data = pix.tobytes("png")
                        img_pil = Image.open(io.BytesIO(img_data))
                        
                        suffix = "_kapak" if not kapak_assigned else ""
                        if not kapak_assigned: kapak_assigned = True
                        
                        page_str = f"{page_num + 1:02d}"
                        output_filename = f"{pdf_base_name}_{page_str}{suffix}.webp"
                        output_filepath = os.path.join(src_dir, output_filename)
                        
                        if img_pil.mode in ("RGBA", "P"):
                            img_pil = img_pil.convert("RGB")
                        img_pil.save(output_filepath, "WEBP", quality=85)
                        
                        # RAM Temizliği
                        del pix, img_data, img_pil
                        gc.collect()
                        
                    doc.close()
                    print(f"✅ {pdf_file} bitti.")
        
        # Standart İşleme ve data.json Güncelleme
        if os.path.exists(src_dir):
            if folder_name not in existing_projects:
                project_data = {"id": folder_name, "year": "2026", "summary": "Açıklama yok.", "previewImages": {}, "detailImages": []}
            else:
                project_data = existing_projects[folder_name]

            # Başlık temizleme
            parts = folder_name.split('_', 1)
            clean_title_base = parts[1] if len(parts) == 2 and parts[0].isdigit() else folder_name
            project_data['title'] = clean_title_base.replace('-', ' ').title()

            thumb_dir = os.path.join(project_dir, 'thumb')
            os.makedirs(thumb_dir, exist_ok=True)
            detail_images = []
            
            valid_exts = ('.jpg', '.jpeg', '.png', '.webp')
            images = sorted([f for f in os.listdir(src_dir) if f.lower().endswith(valid_exts)])

            for img_name in images:
                src_path = os.path.join(src_dir, img_name)
                thumb_path = os.path.join(thumb_dir, img_name)
                
                with Image.open(src_path) as img:
                    width, height = img.size
                    if not os.path.exists(thumb_path):
                        img.thumbnail((800, 800))
                        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                        img.save(thumb_path, "WEBP")
                
                web_src = f"img/projeler/{folder_name}/src/{img_name}"
                web_thumb = f"img/projeler/{folder_name}/thumb/{img_name}"
                
                # Alt metni temizleme
                base_img_name = os.path.splitext(img_name)[0]
                clean_img_name = re.sub(r'(?i)_kapak|_yan1|_yan2', '', base_img_name)
                img_parts = clean_img_name.split('_')
                alt_text = img_parts[-1].replace('-', ' ') if len(img_parts) > 1 and not img_parts[-1].isdigit() else ""

                detail_images.append({"src": web_src, "thumb": web_thumb, "width": width, "height": height, "alt": alt_text})

                if '_kapak' in img_name.lower(): project_data['previewImages']['kapak'] = web_thumb
                elif '_yan1' in img_name.lower(): project_data['previewImages']['yan1'] = web_thumb
                elif '_yan2' in img_name.lower(): project_data['previewImages']['yan2'] = web_thumb
            
            project_data['detailImages'] = detail_images
            updated_projects_list.append(project_data)

# Kaydetme ve Final
updated_projects_list.sort(key=lambda p: get_sort_key(p['id']))
data['projects'] = updated_projects_list
with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n🚀 İşlem Tamamlandı. Tüm veriler güncellendi.")