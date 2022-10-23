import json

from articles.models import Article
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from . import client, utils


@csrf_exempt
def handle_repo_event(request):
    if request.method == "POST":
        headers = request.headers
        signature = headers.get('X-Hub-Signature')
        if signature is None:
            return JsonResponse({"success": False}, status=400)
        try:
            valid_signature = utils.validate_signature(headers, request.body)
        except:
            valid_signature = False
        if signature is None:
            return JsonResponse({"success": False, "signature": "error"}, status=400)
        body = request.body.decode('utf-8')
        json_data = json.loads(body)
        head_commit = json_data.get('head_commit') or {}
        modified_ = head_commit.get('modified') or []
        path = modified_[0] if len(modified_) == 1 else None
        if path is None:
            return JsonResponse({"success": True})
        slug = path.replace("contents/", "").replace(".md", "")
        qs = Article.objects.filter(slug=slug)
        if qs.count() == 1:
            obj = qs.first()
            gh_client = client.ArticleMapper(title=obj.title, slug=slug, content=obj.content)
            content = gh_client.get_repo_file_contents()
            data = utils.extract_markdown_metadata(content)
            header = data.get('header')
            extracted_content = data.get("content")
            if header:
                header_a = f"---\r\n{header}\r\n---"
                header_b = f"---\n{header}\n---"
                header_c = f"---{header}---"
                final_content = content.replace(header_a, '')
                final_content = final_content.replace(header_b, '')
                final_content = final_content.replace(header_c, '')
                final_content = final_content.lstrip()
                qs.update(content=final_content)
    return JsonResponse({"success": True})
