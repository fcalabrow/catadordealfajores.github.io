#!/usr/bin/env python3
"""
Script para corregir los permalinks en los posts.
Remueve el baseurl del permalink (Jekyll lo agrega automáticamente).
"""

import re
from pathlib import Path

POSTS_DIR = Path("_posts")

def fix_permalink_in_post(file_path):
    """Corrige el permalink removiendo el baseurl."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar el permalink actual
        permalink_match = re.search(r'^permalink:\s*(.+)$', content, re.MULTILINE)
        if not permalink_match:
            return False
        
        current_permalink = permalink_match.group(1).strip()
        
        # Extraer el slug del permalink (remover baseurl si existe)
        # Formato actual: /catadordealfajores.github.io/guolis-pistacho/ (o cualquier baseurl)
        # Formato deseado: /guolis-pistacho/
        slug_match = re.search(r'/([^/]+)/?$', current_permalink)
        if not slug_match:
            return False
        
        slug = slug_match.group(1)
        new_permalink = f"/{slug}/"
        
        # Si el permalink ya está correcto, no hacer nada
        if current_permalink == new_permalink:
            return False
        
        # Reemplazar el permalink
        new_content = re.sub(
            r'^permalink:\s*.+$',
            f'permalink: {new_permalink}',
            content,
            flags=re.MULTILINE
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
        
    except Exception as e:
        print(f"  ⚠️  Error procesando {file_path.name}: {e}")
        return False

def main():
    print("🔧 Corrigiendo permalinks en los posts...")
    
    posts_updated = 0
    for post_file in POSTS_DIR.glob("*.md"):
        if fix_permalink_in_post(post_file):
            print(f"  ✓ {post_file.name}")
            posts_updated += 1
    
    print(f"\n✅ {posts_updated} posts actualizados")

if __name__ == "__main__":
    main()


