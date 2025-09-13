import os

DEFAULT_POSTGRES_CONTAINER_IMAGE = "postgres:13"
ASSETS_DIRECTORY = os.path.join(os.path.dirname(__file__), "assets")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
