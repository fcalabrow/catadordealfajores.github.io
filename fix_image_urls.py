#!/usr/bin/env python3
"""
Script para corregir las rutas de imágenes en los posts de Jekyll.
Reemplaza rutas absolutas /assets/images/ con rutas que usan baseurl.
"""

import re
from pathlib import Path

POSTS_DIR = Path("_posts")
BASEURL = "/catador_de_alfajores.github.io"  # Debe coincidir con _config.yml

def fix_image_urls(content):
    """Reemplaza rutas absolutas de imágenes con rutas que usan baseurl."""
    # Patrón para imágenes en Markdown: ![alt](/assets/images/file.jpg)
    # Reemplazar tanto rutas con {{ site.baseurl }} como sin él
    content = re.sub(
        r'(!\[[^\]]*\]\()({{ site\.baseurl }})?(/assets/images/[^\)]+)(\))',
        lambda m: f"{m.group(1)}{BASEURL}{m.group(3)}{m.group(4)}",
        content
    )
    
    # Patrón para imágenes en HTML: <img src="/assets/images/file.jpg">
    content = re.sub(
        r'(<img[^>]+src=["\'])({{ site\.baseurl }})?(/assets/images/[^"\']+)(["\'])',
        lambda m: f"{m.group(1)}{BASEURL}{m.group(3)}{m.group(4)}",
        content
    )
    
    # Patrón para URLs directas: /assets/images/file.jpg (solo si no tienen baseurl ya)
    content = re.sub(
        r'(\s|"|\'|\(|\[)(/assets/images/[^\s"\'\)\]>]+)',
        lambda m: f"{m.group(1)}{BASEURL}{m.group(2)}" if BASEURL not in m.group(0) else m.group(0),
        content
    )
    
    return content

def main():
    print("🔧 Corrigiendo rutas de imágenes en posts...")
    
    posts_fixed = 0
    for post_file in POSTS_DIR.glob("*.md"):
        try:
            with open(post_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            content = fix_image_urls(content)
            
            if content != original_content:
                with open(post_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✓ {post_file.name}")
                posts_fixed += 1
        except Exception as e:
            print(f"  ⚠️  Error procesando {post_file.name}: {e}")
    
    print(f"\n✅ {posts_fixed} posts actualizados")

if __name__ == "__main__":
    main()

