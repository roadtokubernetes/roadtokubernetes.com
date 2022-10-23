import hashlib
import hmac
import re

from django.conf import settings
from django.template.loader import render_to_string


def validate_signature(headers, body):
    # Get the signature from the payload
    secret = settings.GH_WEBHOOK_SECRET
    signature_header = headers.get('X-Hub-Signature')
    sha_name, github_signature = signature_header.split('=')
    if sha_name != 'sha1':
        print('ERROR: X-Hub-Signature in payload headers was not sha1=****')
        return False
      
    # Create our own signature
    local_signature = hmac.new(secret.encode('utf-8'), msg=body, digestmod=hashlib.sha1)

    # See if they match
    return hmac.compare_digest(local_signature.hexdigest(), github_signature)


def extract_markdown_metadata(content):
    regex = r'^---\r?\n?(?P<header>.*?)\r?\n?---(?P<content>.*)'
    r = re.compile(regex, flags=re.DOTALL)
    match = r.match(content)
    if not match:
        return {}
    return match.groupdict()
