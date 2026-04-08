import os
import json
import re
import fitz  # PyMuPDF kütüphanesi
import io
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
        
        # --- ÇOKLU PDF DESTEĞİ VE SIRALAMA ---
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
                    print(f"📄 PDF bulundu ve sırayla işleniyor: {pdf_file}")
                    doc = fitz.open(pdf_path)
                    
                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        mat = fitz.Matrix(2.0, 2.0)
                        pix = page.get_pixmap(matrix=mat)
                        
                        img_data = pix.tobytes("png")
                        img_pil = Image.open(io.BytesIO(img_data))
                        
                        suffix = ""
                        if not kapak_assigned:
                            suffix = "_kapak"
                            kapak_assigned = True
                        
                        page_str = f"{page_num + 1:02d}"
                        output_filename = f"{pdf_base_name}_{page_str}{suffix}.webp"
                        output_filepath = os.path.join(src_dir, output_filename)
                        
                        if img_pil.mode in ("RGBA", "P"):
                            img_pil = img_pil.convert("RGB")
                        img_pil.save(output_filepath, "WEBP", quality=85)
                        
                        existing_src_files.append(output_filename)
                        
                    doc.close()
                    print(f"✅ {pdf_file} başarıyla aktarıldı.")
                else:
                    print(f"⏭️ {pdf_file} zaten işlenmiş, atlanıyor.")
        # --------------------------------------------------------

        # ESKİ USUL İŞLEYİŞ
        if os.path.exists(src_dir):
            
            if folder_name not in existing_projects:
                print(f"🌟 Yeni proje keşfedildi ve sisteme ekleniyor: {folder_name}")
                project_data = {
                    "id": folder_name,
                    "year": "2026",
                    "summary": "Bu proje için henüz bir açıklama girilmedi.",
                    "previewImages": {},
                    "detailImages": []
                }
            else:
                project_data = existing_projects[folder_name]

            # --- KÖKLÜ ÇÖZÜM: BAŞLIĞI HER ÇALIŞMADA ZORLA GÜNCELLE ---
            parts = folder_name.split('_', 1)
            if len(parts) == 2 and parts[0].isdigit():
                clean_title_base = parts[1]
            else:
                clean_title_base = folder_name
            
            title_guess = clean_title_base.replace('-', ' ').title()
            project_data['title'] = title_guess
            
            # GÖRSEL KONTROL: Botun ne yaptığını terminale yazdırıyoruz
            print(f"✏️ Sistem Başlığı Düzeltildi: [{folder_name}] ---> [{title_guess}]")
            # ---------------------------------------------------------

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
                        img.save(thumb_path, format="JPEG" if img_lower.endswith('.jpg') else "WEBP")
                
                web_src = f"img/projeler/{folder_name}/src/{img_name}"
                web_thumb = f"img/projeler/{folder_name}/thumb/{img_name}"
                
                base_name = os.path.splitext(img_name)[0]
                clean_name = re.sub(r'(?i)_kapak|_yan1|_yan2', '', base_name)
                parts_img = clean_name.split('_')
                
                alt_text = ""
                if len(parts_img) > 1:
                    last_part = parts_img[-1]
                    if not last_part.isdigit() and len(last_part) > 1:
                        alt_text = last_part.replace('-', ' ')

                detail_images.append({
                    "src": web_src,
                    "thumb": web_thumb,
                    "width": width,
                    "height": height,
                    "alt": alt_text
                })

                if '_kapak' in img_lower:
                    project_data['previewImages']['kapak'] = web_thumb
                elif '_yan1' in img_lower:
                    project_data['previewImages']['yan1'] = web_thumb
                elif '_yan2' in img_lower:
                    project_data['previewImages']['yan2'] = web_thumb
            
            project_data['detailImages'] = detail_images
            updated_projects_list.append(project_data)

updated_projects_list.sort(key=lambda p: get_sort_key(p['id']))

data['projects'] = updated_projects_list

with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n🚀 Mükemmel! Eski başlıklar temizlendi, projeler sıralandı ve data.json güncellendi.")