# Generador de Jekyll para usar campo 'slug' en permalinks
# Compatible con GitHub Pages

module Jekyll
  class SlugPermalinkGenerator < Generator
    safe true
    priority :lowest

    def generate(site)
      return unless site.config['permalink'] && site.config['permalink'].include?(':slug')
      
      site.posts.docs.each do |post|
        if post.data['slug']
          # Crear un permalink personalizado usando el slug
          slug = post.data['slug']
          url_template = site.config['permalink'].dup
          url = url_template.gsub(':slug', slug)
          url = url.gsub(':year', post.date.strftime('%Y'))
          url = url.gsub(':month', post.date.strftime('%m'))
          url = url.gsub(':day', post.date.strftime('%d'))
          url = url.gsub(':title', post.data['slug'] || post.slug)
          url = url.gsub(':categories', (post.data['categories'] || []).join('/'))
          url = url.gsub(':name', post.basename_without_ext)
          
          # Asignar el permalink personalizado
          post.data['permalink'] = url
        end
      end
    end
  end
end
