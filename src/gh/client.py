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
    debug_mode: bool = settings.DJANGO_DEBUG
    publish_timestamp: datetime = None
    tags: List[str] = None
    api_directory: str = "contents"
    api_message: str = "Updated article."
    api_endpoint: str = ""

    def __post_init__(self):
        path = f"{self.api_directory}/{self.slug}.md"
        self.api_endpoint = ENDPOINT.format(url=BASE_URL, repo=REPO, path=path)

    @property
    def _headers(self):
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GH_BLOG_TOKEN}",
        }

    def get_repo_file(self, raw_request=False):
        r = requests.get(self.api_endpoint, headers=self._headers)
        if raw_request:
            return r
        if r.status_code == 404:
            return None
        return r.json()

    def get_repo_file_contents(self):
        r = self.get_repo_file(raw_request=True)
        if r.status_code != 200:
            return ""
        data = r.json()
        content = data.get("content") or None
        if content is None:
            return ""
        try:
            return base64.b64decode(content).decode("utf-8")
        except:
            pass

    def get_prev_sha(self):
        data = self.get_repo_file()
        if data is None:
            return None
        return data.get("sha")

    def get_encoded_content(self):
        markdown_content = render_to_string(
            "gh/article_base.md",
            {
                "title": self.title,
                "author": self.author,
                "slug": self.slug,
                "publish_timestamp": self.publish_timestamp,
                "url": self.url,
                "tags": self.tags,
                "content": self.content,
            },
        )
        markdown_content_bytes = markdown_content.encode()
        content_encoded = base64.b64encode(markdown_content_bytes).decode()
        return content_encoded

    def save(self):
        data = json.dumps(
            {
                "message": self.api_message,
                "content": self.get_encoded_content(),
                "sha": self.get_prev_sha(),
            }
        )
        if self.debug_mode:
            return {}
        r = requests.put(self.api_endpoint, headers=self._headers, data=data)
        created = r.status_code == 201
        updated = r.status_code == 200
        error = r.status_code not in range(200, 299)
        return {
            "response": r.json(),
            "created": created,
            "updated": updated,
            "error": error,
        }
