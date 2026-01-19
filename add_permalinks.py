#!/usr/bin/env python3
"""
Script para agregar permalink al front matter de cada post.
Usa el campo 'slug' para crear el permalink correcto.
"""

import re
from pathlib import Path

POSTS_DIR = Path("_posts")
BASEURL = ""  # Vacío para repositorio catadordealfajores.github.io

def add_permalink_to_post(file_path):
    """Agrega el permalink al front matter del post."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar si ya tiene permalink
        if 'permalink:' in content:
            return False
        
        # Buscar el slug en el front matter
        slug_match = re.search(r'^slug:\s*(.+)$', content, re.MULTILINE)
        if not slug_match:
            return False
        
        slug = slug_match.group(1).strip()
        
        # Crear permalink (sin baseurl, Jekyll lo agrega automáticamente)
        permalink = f"/{slug}/"
        
        # Buscar el front matter (entre --- y ---)
        front_matter_pattern = r'^(---\s*\n)(.*?)(\n---\s*\n)'
        match = re.match(front_matter_pattern, content, re.DOTALL)
        
        if not match:
            return False
        
        front_matter = match.group(2)
        body = content[match.end():]
        
        # Agregar permalink después del slug
        if 'slug:' in front_matter:
            # Insertar después de slug
            front_matter = re.sub(
                r'(slug:.*\n)',
                r'\1permalink: ' + permalink + '\n',
                front_matter
            )
        else:
            # Agregar al final del front matter
            front_matter += '\npermalink: ' + permalink
        
        # Reconstruir el contenido
        new_content = match.group(1) + front_matter + match.group(3) + body
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
        
    except Exception as e:
        print(f"  ⚠️  Error procesando {file_path.name}: {e}")
        return False

def main():
    print("🔧 Agregando permalinks a los posts...")
    
    posts_updated = 0
    for post_file in POSTS_DIR.glob("*.md"):
        if add_permalink_to_post(post_file):
            print(f"  ✓ {post_file.name}")
            posts_updated += 1
    
    print(f"\n✅ {posts_updated} posts actualizados con permalink")

if __name__ == "__main__":
    main()

