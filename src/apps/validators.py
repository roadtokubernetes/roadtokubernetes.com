from urllib.parse import urlparse

from django.core.validators import URLValidator

url_validator = URLValidator(schemes=["http", "https"])
