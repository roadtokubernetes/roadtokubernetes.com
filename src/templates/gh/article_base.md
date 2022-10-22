---
title: {{ title }}
{% if author %}author: {{ author }}{% endif %}
{% if publish_timestamp %}publish_timestamp: {{ publish_timestamp }}{% endif %}
{% if tags and tags.length > 0 %}tags: [{% for tag in tags %}{{ tag }},{% endfor %}]{% endif %}
---
# {% if url %}[{{ title }}]({{ url }}){% else %}{{ title }}{% endif %}
{% if url %}[Original Post]({{ url }}){% endif %}

{{ content }}