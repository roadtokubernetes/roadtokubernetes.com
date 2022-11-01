from urllib.parse import urlparse

from django.core.validators import URLValidator

url_validator = URLValidator(schemes=["http", "https"])


def validate_replica_count(value):
    if value < 0:
        raise ValueError(f"{value} is too small. You must select 0 or higher")
    return value
