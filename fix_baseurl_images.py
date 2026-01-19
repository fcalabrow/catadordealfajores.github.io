#!/usr/bin/env python3
"""
Script para agregar {{ site.baseurl }} a las rutas de imágenes en los posts.
"""

import re
from pathlib import Path

POSTS_DIR = Path("_posts")

def fix_image_urls(content):
    """Agrega {{ site.baseurl }} a las rutas de imágenes."""
    # Patrón para imágenes en Markdown: ![](/assets/images/file.jpg)
    # o ![alt](/assets/images/file.jpg)
    content = re.sub(
        r'!\[([^\]]*)\]\((/assets/images/[^\)]+)\)',
        r'![\1]({{ site.baseurl }}\2)',
        content
    )
    
    return content

def main():
    print("🔧 Agregando {{ site.baseurl }} a las rutas de imágenes...")
    
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

