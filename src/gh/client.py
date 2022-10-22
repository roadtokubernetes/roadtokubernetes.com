import base64
import json
from dataclasses import dataclass
from datetime import datetime
from typing import List

import requests
from django.conf import settings
from django.template.loader import render_to_string

BASE_URL = "https://api.github.com"
REPO = "roadtokubernetes/blog"
ENDPOINT = "{url}/repos/{repo}/contents/{path}"
GH_BLOG_TOKEN = settings.GH_BLOG_TOKEN

@dataclass
class ArticleMapper:
    slug: str
    title: str
    content: str
    url: str = None
    author: str = None
    publish_timestamp: datetime = None
    tags: List[str] = None
    api_directory: str = "contents"
    api_message: str = "Updated article."
    api_endpoint: str = ""
    

    def __post_init__(self):
        path = f"{self.api_directory}/{self.slug}.md"
        self.api_endpoint = ENDPOINT.format(
            url=BASE_URL,
            repo=REPO,
            path=path
        )
        

    @property
    def _headers(self):
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GH_BLOG_TOKEN}"
        }
    
    def get_prev_sha(self):
        r = requests.get(self.api_endpoint, headers=self._headers)
        if r.status_code == 404:
            return ""
        return r.json().get('sha')
    
    def get_encoded_content(self):
        markdown_content = render_to_string("gh/article_base.md", {
            "title": self.title,
            "author": self.author,
            "publish_timestamp": self.publish_timestamp,
            "url": self.url,
            "tags": self.tags,
            "content": self.content
        })
        markdown_content_bytes = markdown_content.encode()
        content_encoded = base64.b64encode(markdown_content_bytes).decode()
        return content_encoded
    
    def save(self):
        data = json.dumps({
            "message": self.api_message,
            "content": self.get_encoded_content(),
            "sha": self.get_prev_sha()
        })
        r = requests.put(self.api_endpoint, headers=self._headers, data=data)
        created = r.status_code == 201
        updated = r.status_code == 200
        error = r.status_code not in range(200, 299)
        return {
            "response": r.json(), 
            "created": created, 
            "updated": updated, 
            "error": error
        }

        
