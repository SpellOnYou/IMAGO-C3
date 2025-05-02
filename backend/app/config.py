import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Elasticsearch configuration
ELASTICSEARCH_CONFIG = {
    "hosts": [os.getenv("ELASTICSEARCH_HOST")],
    "basic_auth": (
        os.getenv("ELASTICSEARCH_USERNAME"),
        os.getenv("ELASTICSEARCH_PASSWORD")
    ),
    "verify_certs": False
}
