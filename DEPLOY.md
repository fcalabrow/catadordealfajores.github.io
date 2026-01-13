# Guía de Deploy a GitHub Pages

## Paso 1: Renombrar repositorio (si es necesario)

Si tu repositorio se llama `catador_de_alfajores` y quieres que la URL sea `catador_de_alfajores.github.io`:

1. Ve a tu repositorio en GitHub
2. Click en "Settings" (Configuración)
3. Scroll hasta "Repository name"
4. Cambia el nombre a: `catador_de_alfajores.github.io`
5. Click en "Rename"

**Nota**: Para que funcione `catador_de_alfajores.github.io`, el repositorio DEBE llamarse exactamente `catador_de_alfajores.github.io`

**Alternativa**: Si prefieres mantener el nombre `catador_de_alfajores`, la URL será `TU_USUARIO.github.io/catador_de_alfajores` y necesitarás actualizar `_config.yml` con:
- `url: https://TU_USUARIO.github.io`
- `baseurl: "/catador_de_alfajores"`

## Paso 2: Configurar el repositorio local

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
# Si el repo ya existe, solo necesitas agregar y hacer push
git add .

# Hacer commit inicial (o agregar cambios)
git commit -m "Migración inicial de WordPress a Jekyll"

# Si aún no tienes el remote configurado:
# git remote add origin https://github.com/TU_USUARIO/catador_de_alfajores.github.io.git

# Subir a GitHub
git branch -M main  # Si no estás en main
git push -u origin main
```

## Paso 3: Configurar GitHub Pages

1. Ve a tu repositorio en GitHub
2. Click en "Settings" (Configuración)
3. En el menú lateral, click en "Pages"
4. En "Source", selecciona "Deploy from a branch"
5. Selecciona la rama "main" y la carpeta "/ (root)"
6. Click en "Save"

## Paso 4: Configurar Jekyll en GitHub Pages

GitHub Pages automáticamente detectará que es un sitio Jekyll y lo construirá. El `_config.yml` ya está configurado con `url: https://catador_de_alfajores.github.io`.

**Opcional**: Crear archivo `.github/workflows/jekyll.yml` para más control:

```yaml
name: Jekyll site builder

on:
  push:
    branches:
      - main

jobs:
  github-pages:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-ruby@v1
        with:
          ruby-version: '3.1'
          bundler-cache: true
      - uses: helaili/jekyll-action@v2
        with:
          jekyll_src: '.'
```

3. Hacer commit y push de estos cambios

## Paso 5: Esperar el deploy

- GitHub Pages tarda unos minutos en construir el sitio
- Verás un mensaje verde en tu repositorio cuando esté listo
- Tu sitio estará disponible en: `https://catador_de_alfajores.github.io`

## Paso 6: Personalizar (Opcional)

### Agregar un tema

1. Edita `Gemfile` y descomenta un tema (ej: `jekyll-theme-minima`)
2. Edita `_config.yml` y agrega: `theme: minima`
3. Ejecuta `bundle install` localmente
4. Haz commit y push

### Personalizar layout

Crea una carpeta `_layouts/` y personaliza los layouts según necesites.

### Agregar navegación

Crea un archivo `_includes/header.html` o `_includes/navigation.html` con tu menú.

## Troubleshooting

### El sitio no aparece
- Espera 5-10 minutos después del primer push
- Verifica que el repositorio se llame exactamente `catador_de_alfajores.github.io`
- Si el repo se llama solo `catador_de_alfajores`, renómbralo a `catador_de_alfajores.github.io`
- Revisa la pestaña "Actions" en GitHub para ver si hay errores

### Errores de build
- Revisa los logs en "Actions" → tu workflow
- Verifica que `_config.yml` esté bien formateado
- Asegúrate de que todos los posts tengan front matter válido

### Imágenes no aparecen
- Verifica que las rutas en los posts sean `/assets/images/nombre.jpg`
- Asegúrate de que la carpeta `assets/images/` esté en el repositorio

## Próximos pasos

1. Personalizar el diseño con un tema de Jekyll
2. Configurar un dominio personalizado (si lo deseas)
3. Agregar Google Analytics (opcional)
4. Configurar comentarios con Disqus o similar (opcional)

