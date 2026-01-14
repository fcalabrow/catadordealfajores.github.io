---
layout: default
title: Catador de alfajores
---

# Catador de alfajores

Bienvenido al blog sobre alfajores argentinos.

## Posts recientes

{% for post in site.posts limit:10 %}
- [{{ post.title }}]({{ site.baseurl }}{{ post.url }}) - {{ post.date | date: "%d/%m/%Y" }}
{% endfor %}

{% if site.posts.size > 10 %}
<p><a href="{{ site.baseurl }}/posts">Ver todos los posts ({{ site.posts.size }} total)</a></p>
{% endif %}

