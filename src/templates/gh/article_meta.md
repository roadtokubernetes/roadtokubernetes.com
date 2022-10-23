---
title: {{ title }}
slug: {{ slug }}
{% if author %}author: {{ author }}{% endif %}
{% if publish_timestamp %}publish_timestamp: {{ publish_timestamp }}{% endif %}
{% if url %}url: {{ url }}{% endif %}
{% if tags and tags.length > 0 %}tags: [{% for tag in tags %}{{ tag }},{% endfor %}]{% endif %}
---