#!/usr/bin/env python3
"""
Script para convertir exportación XML de WordPress a archivos Markdown para Jekyll.
- Extrae solo posts publicados (omite drafts, attachments, etc.)
- Omite todos los comentarios
- Convierte HTML a Markdown
- Descarga imágenes y actualiza referencias
- Genera front matter de Jekyll con metadatos
"""

import xml.etree.ElementTree as ET
import html2text
import re
import os
import requests
from pathlib import Path
from urllib.parse import urlparse, unquote
from datetime import datetime
import json
from PIL import Image
import io

# Configuración
XML_FILE = "catadordealfajores.WordPress.2026-01-13.xml"
OUTPUT_DIR = Path("_posts")
IMAGES_DIR = Path("assets/images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MAX_IMAGE_SIZE_MB = 1.0  # Comprimir imágenes mayores a 1MB
IMAGE_QUALITY = 85  # Calidad para JPEG (1-100)

# Configurar html2text
h = html2text.HTML2Text()
h.ignore_links = False
h.ignore_images = False
h.body_width = 0  # No wrap lines
h.unicode_snob = True

def sanitize_filename(filename):
    """Convierte un string a un nombre de archivo válido."""
    # Remover caracteres especiales
    filename = re.sub(r'[^\w\s-]', '', filename)
    # Reemplazar espacios con guiones
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename.lower()

def compress_image(image_path, max_size_mb=MAX_IMAGE_SIZE_MB, initial_quality=IMAGE_QUALITY):
    """Comprime una imagen iterativamente hasta que sea menor al tamaño máximo especificado."""
    try:
        file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
        original_size_mb = file_size_mb
        
        if file_size_mb <= max_size_mb:
            return False  # No necesita compresión
        
        # Abrir imagen
        img = Image.open(image_path)
        original_size = img.size
        
        # Convertir a RGB si es necesario (para JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Crear fondo blanco para imágenes con transparencia
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = rgb_img
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Determinar si necesitamos cambiar la extensión
        needs_extension_change = image_path.suffix.lower() in ['.png', '.gif', '.webp']
        if needs_extension_change:
            final_path = image_path.with_suffix('.jpg')
        else:
            final_path = image_path
        
        # Compresión iterativa hasta que sea menor a max_size_mb
        quality = initial_quality
        max_dimension = 2048
        iteration = 0
        max_iterations = 10  # Límite de seguridad
        
        while file_size_mb > max_size_mb and iteration < max_iterations:
            iteration += 1
            working_img = img.copy()
            
            # Redimensionar si es necesario (reducir dimensiones progresivamente)
            current_max_dim = max(working_img.size)
            if current_max_dim > max_dimension:
                ratio = max_dimension / current_max_dim
                new_size = (int(working_img.size[0] * ratio), int(working_img.size[1] * ratio))
                working_img = working_img.resize(new_size, Image.Resampling.LANCZOS)
                if iteration == 1:
                    print(f"    📐 Redimensionada a {new_size[0]}x{new_size[1]}")
            
            # Guardar con calidad actual
            working_img.save(final_path, 'JPEG', quality=quality, optimize=True)
            
            # Verificar nuevo tamaño
            file_size_mb = os.path.getsize(final_path) / (1024 * 1024)
            
            # Si aún es muy grande, reducir calidad y dimensiones
            if file_size_mb > max_size_mb:
                quality = max(50, quality - 10)  # Reducir calidad en pasos de 10, mínimo 50
                max_dimension = int(max_dimension * 0.9)  # Reducir dimensiones en 10%
                if iteration == 1:
                    print(f"    🔄 Comprimiendo iterativamente...")
            else:
                break
        
        # Si cambió la extensión, eliminar archivo original
        if needs_extension_change and final_path != image_path:
            if image_path.exists():
                os.remove(image_path)
            return True, final_path
        
        # Verificar que finalmente sea menor a max_size_mb
        final_size_mb = os.path.getsize(final_path) / (1024 * 1024)
        if final_size_mb > max_size_mb:
            print(f"    ⚠️  Advertencia: Imagen aún pesa {final_size_mb:.2f}MB después de compresión")
            # Último intento: redimensionar más agresivamente
            working_img = Image.open(final_path)
            target_ratio = (max_size_mb / final_size_mb) ** 0.5  # Raíz cuadrada para reducir área
            new_size = (int(working_img.size[0] * target_ratio), int(working_img.size[1] * target_ratio))
            working_img = working_img.resize(new_size, Image.Resampling.LANCZOS)
            working_img.save(final_path, 'JPEG', quality=60, optimize=True)
            final_size_mb = os.path.getsize(final_path) / (1024 * 1024)
        
        reduction = ((original_size_mb - final_size_mb) / original_size_mb) * 100
        print(f"    🗜️  Comprimida: {original_size_mb:.2f}MB → {final_size_mb:.2f}MB ({reduction:.1f}% reducción)")
        
        return True
        
    except Exception as e:
        print(f"    ⚠️  Error comprimiendo {image_path}: {e}")
        return False

def download_image(url, output_path):
    """Descarga una imagen desde una URL y la comprime si es necesario."""
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        response.raise_for_status()
        
        # Guardar imagen
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        # Comprimir si es necesario
        result = compress_image(output_path)
        
        # Si la compresión cambió el archivo (extensión), retornar el nuevo path
        if isinstance(result, tuple):
            return (True, result[1])
        elif result:
            # Se comprimió pero no cambió el nombre
            return (True, output_path)
        else:
            # No se comprimió (ya era pequeña o error)
            return (True, output_path)
        
    except Exception as e:
        print(f"  ⚠️  Error descargando {url}: {e}")
        return (False, None)

def extract_image_urls(content):
    """Extrae todas las URLs de imágenes del contenido HTML."""
    urls = set()
    
    # Buscar en tags img
    img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
    matches = re.findall(img_pattern, content, re.IGNORECASE)
    urls.update(matches)
    
    # Buscar en wp:image blocks y otros src
    wp_image_pattern = r'src=["\']([^"\']+\.(?:jpg|jpeg|png|gif|webp|svg))["\']'
    matches = re.findall(wp_image_pattern, content, re.IGNORECASE)
    # re.findall retorna tuplas cuando hay grupos, solo tomar el primer elemento
    urls.update([m if isinstance(m, str) else m[0] for m in matches])
    
    # Buscar URLs directas en el contenido (sin grupos de captura)
    url_pattern = r'(https?://[^\s<>"]+\.(?:jpg|jpeg|png|gif|webp|svg))'
    matches = re.findall(url_pattern, content, re.IGNORECASE)
    urls.update(matches)
    
    return list(urls)

def process_image_url(url, base_url):
    """Procesa una URL de imagen: la descarga y retorna la nueva ruta relativa."""
    if not url or not url.startswith('http'):
        return url
    
    # Parsear URL
    parsed = urlparse(url)
    path = unquote(parsed.path)
    
    # Extraer nombre de archivo
    filename = os.path.basename(path)
    if not filename:
        filename = "image.jpg"
    
    # Crear ruta de salida
    output_path = IMAGES_DIR / filename
    
    # Si la imagen ya existe, verificar si necesita compresión
    if output_path.exists():
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        if file_size_mb > MAX_IMAGE_SIZE_MB:
            print(f"  🔧 Imagen existente necesita compresión: {filename} ({file_size_mb:.2f}MB)")
            result = compress_image(output_path)
            if isinstance(result, tuple):
                # La compresión cambió la extensión
                final_path = result[1]
                final_filename = final_path.name if isinstance(final_path, Path) else os.path.basename(str(final_path))
                return f"/assets/images/{final_filename}"
            else:
                return f"/assets/images/{filename}"
        else:
            print(f"  ✓ Imagen ya existe y está optimizada: {filename}")
            return f"/assets/images/{filename}"
    
    # Descargar imagen
    print(f"  📥 Descargando: {filename}")
    result = download_image(url, output_path)
    
    if result[0]:  # Descarga exitosa
        final_path = result[1]
        if isinstance(final_path, Path):
            final_filename = final_path.name
        else:
            final_filename = os.path.basename(str(final_path))
        return f"/assets/images/{final_filename}"
    else:
        # Si falla la descarga, mantener URL original
        return url

def replace_image_urls(content, base_url):
    """Reemplaza URLs de imágenes en el contenido."""
    image_urls = extract_image_urls(content)
    
    for url in image_urls:
        new_url = process_image_url(url, base_url)
        # Reemplazar todas las ocurrencias
        content = content.replace(url, new_url)
    
    return content

def get_post_categories(item):
    """Extrae las categorías de un post."""
    categories = []
    for category in item.findall('.//category'):
        domain = category.get('domain')
        if domain == 'category':
            cat_name = category.text
            if cat_name:
                categories.append(cat_name)
    return categories

def get_post_tags(item):
    """Extrae los tags de un post."""
    tags = []
    for category in item.findall('.//category'):
        domain = category.get('domain')
        if domain == 'post_tag':
            tag_name = category.text
            if tag_name:
                tags.append(tag_name)
    return tags

def format_date_for_jekyll(date_str):
    """Convierte fecha de WordPress a formato Jekyll (YYYY-MM-DD HH:MM:SS)."""
    try:
        # WordPress usa formato: 2024-02-20 22:04:59
        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return date_str

def convert_post_to_markdown(item):
    """Convierte un item de WordPress a Markdown para Jekyll."""
    # Verificar que sea un post publicado
    post_type = item.find('.//{http://wordpress.org/export/1.2/}post_type')
    if post_type is None or post_type.text != 'post':
        return None
    
    status = item.find('.//{http://wordpress.org/export/1.2/}status')
    if status is None or status.text != 'publish':
        return None
    
    # Extraer metadatos
    title_elem = item.find('title')
    title = title_elem.text if title_elem is not None else "Sin título"
    
    post_date = item.find('.//{http://wordpress.org/export/1.2/}post_date')
    date_str = post_date.text if post_date is not None else ""
    
    post_name = item.find('.//{http://wordpress.org/export/1.2/}post_name')
    slug = post_name.text if post_name is not None else ""
    
    creator = item.find('.//{http://purl.org/dc/elements/1.1/}creator')
    author = creator.text if creator is not None else ""
    
    # Extraer contenido
    content_elem = item.find('.//{http://purl.org/rss/1.0/modules/content/}encoded')
    if content_elem is None:
        return None
    
    content_html = content_elem.text or ""
    
    # Procesar imágenes
    content_html = replace_image_urls(content_html, "")
    
    # Convertir HTML a Markdown
    content_md = h.handle(content_html)
    
    # Limpiar el markdown (remover líneas vacías excesivas)
    content_md = re.sub(r'\n{3,}', '\n\n', content_md)
    content_md = content_md.strip()
    
    # Extraer categorías y tags
    categories = get_post_categories(item)
    tags = get_post_tags(item)
    
    # Crear front matter
    front_matter = {
        'layout': 'post',
        'title': title,
        'date': format_date_for_jekyll(date_str),
        'author': author,
    }
    
    if categories:
        front_matter['categories'] = categories
    if tags:
        front_matter['tags'] = tags
    
    # Formatear front matter como YAML
    yaml_lines = ['---']
    for key, value in front_matter.items():
        if isinstance(value, list):
            yaml_lines.append(f"{key}:")
            for item in value:
                yaml_lines.append(f"  - {item}")
        else:
            yaml_lines.append(f"{key}: {value}")
    yaml_lines.append('---')
    
    # Crear nombre de archivo
    if slug:
        filename = f"{date_str[:10]}-{slug}.md"
    else:
        filename = f"{date_str[:10]}-{sanitize_filename(title)}.md"
    
    # Crear contenido final
    markdown_content = '\n'.join(yaml_lines) + '\n\n' + content_md
    
    return {
        'filename': filename,
        'content': markdown_content,
        'title': title
    }

def main():
    print("🚀 Iniciando conversión de WordPress a Jekyll...")
    print(f"📂 Leyendo: {XML_FILE}")
    
    # Parsear XML
    try:
        tree = ET.parse(XML_FILE)
        root = tree.getroot()
    except Exception as e:
        print(f"❌ Error parseando XML: {e}")
        return
    
    # Namespace
    namespaces = {
        'content': 'http://purl.org/rss/1.0/modules/content/',
        'wp': 'http://wordpress.org/export/1.2/',
        'dc': 'http://purl.org/dc/elements/1.1/',
    }
    
    # Encontrar todos los items
    items = root.findall('.//item')
    print(f"📝 Encontrados {len(items)} items en total")
    
    # Procesar posts
    posts_processed = 0
    posts_skipped = 0
    
    for item in items:
        result = convert_post_to_markdown(item)
        
        if result is None:
            posts_skipped += 1
            continue
        
        # Guardar archivo
        output_path = OUTPUT_DIR / result['filename']
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result['content'])
            print(f"✓ {result['filename']}: {result['title']}")
            posts_processed += 1
        except Exception as e:
            print(f"❌ Error guardando {result['filename']}: {e}")
    
    # Verificación final: asegurar que ninguna imagen sea mayor a 1MB
    print(f"\n🔍 Verificando tamaño de imágenes...")
    large_images = []
    for img_file in IMAGES_DIR.glob('*'):
        if img_file.is_file():
            size_mb = img_file.stat().st_size / (1024 * 1024)
            if size_mb > MAX_IMAGE_SIZE_MB:
                large_images.append((img_file, size_mb))
    
    if large_images:
        print(f"   ⚠️  Encontradas {len(large_images)} imágenes mayores a {MAX_IMAGE_SIZE_MB}MB, comprimiendo...")
        for img_path, size_mb in large_images:
            print(f"   🔧 Comprimiendo: {img_path.name} ({size_mb:.2f}MB)")
            compress_image(img_path, max_size_mb=MAX_IMAGE_SIZE_MB, initial_quality=60)
        
        # Verificar nuevamente
        still_large = []
        for img_file in IMAGES_DIR.glob('*'):
            if img_file.is_file():
                size_mb = img_file.stat().st_size / (1024 * 1024)
                if size_mb > MAX_IMAGE_SIZE_MB:
                    still_large.append((img_file, size_mb))
        
        if still_large:
            print(f"   ⚠️  Advertencia: {len(still_large)} imágenes aún son mayores a {MAX_IMAGE_SIZE_MB}MB")
            for img_path, size_mb in still_large:
                print(f"      - {img_path.name}: {size_mb:.2f}MB")
        else:
            print(f"   ✅ Todas las imágenes ahora son menores a {MAX_IMAGE_SIZE_MB}MB")
    else:
        print(f"   ✅ Todas las imágenes son menores a {MAX_IMAGE_SIZE_MB}MB")
    
    print(f"\n✅ Conversión completada!")
    print(f"   Posts procesados: {posts_processed}")
    print(f"   Items omitidos: {posts_skipped}")
    print(f"   Archivos guardados en: {OUTPUT_DIR}")
    print(f"   Imágenes guardadas en: {IMAGES_DIR}")

if __name__ == "__main__":
    main()

