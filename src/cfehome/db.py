from decouple import config

DJANGO_DEBUG = config("DJANGO_DEBUG", default=False)
POSTGRES_USER = config("POSTGRES_USER", default=None)
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", default=None)
POSTGRES_DB = config("POSTGRES_DB", default=None)
POSTGRES_HOST = config("POSTGRES_HOST", default=None)
POSTGRES_PORT = config("POSTGRES_PORT", default=None)
POSTGRES_DB_IS_AVAIL = all(
    [POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT]
)
POSTGRES_DB_REQUIRE_SSL = config("POSTGRES_DB_REQUIRE_SSL", cast=bool, default=False)

if DJANGO_DEBUG:
    print(f"DB using {POSTGRES_HOST}:{POSTGRES_PORT}")
if POSTGRES_DB_IS_AVAIL:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": POSTGRES_DB,
            "USER": POSTGRES_USER,
            "PASSWORD": POSTGRES_PASSWORD,
            "HOST": POSTGRES_HOST,
            "PORT": POSTGRES_PORT,
        }
    }
    if POSTGRES_DB_REQUIRE_SSL:
        DATABASES["default"]["OPTIONS"] = {"sslmode": "require"}
