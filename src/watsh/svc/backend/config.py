import os
import pkg_resources
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Utility function to fetch environment variables
def get_env_variable(key: str, default: str = None, required: bool = False) -> str:
    value = os.getenv(key, default)
    if required and value is None:
        raise EnvironmentError(f"Required environment variable {key} not set.")
    return value

# Application Information
VERSION = pkg_resources.get_distribution('watsh.svc.backend').version

# Server Configuration
SERVER_HOST = get_env_variable('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(get_env_variable('SERVER_PORT', '80'))
SERVER_RELOAD = get_env_variable('SERVER_RELOAD', 'true').lower() == 'true'
SERVER_PROXY_HEADER = get_env_variable('SERVER_PROXY_HEADER', 'true').lower() == 'true'

# Security and Authentication
AES_SECRET = get_env_variable('AES_SECRET', required=True)
JWT_SECRET = get_env_variable('JWT_SECRET', required=True)
JWT_ALGORITHM = get_env_variable('JWT_ALGORITHM', 'HS256')
MIDDLEWARE_SESSION_SECRET = get_env_variable('MIDDLEWARE_SESSION_SECRET', required=True)

# Database Configuration
MONGO_URI = get_env_variable('MONGO_URI', required=True)

# Email Server Settings
SMTP_USERNAME = get_env_variable('SMTP_USERNAME', required=True)
SMTP_PASSWORD = get_env_variable('SMTP_PASSWORD', required=True)
SMTP_HOST = get_env_variable('SMTP_HOST', required=True)
SMTP_PORT = get_env_variable('SMTP_PORT', required=True)
SMTP_FROM_EMAIL = get_env_variable('SMTP_FROM_EMAIL', SMTP_USERNAME)

# Logging Configuration
LOGGING_LEVEL = get_env_variable('LOGGING_LEVEL', 'DEBUG')
LOGGING_FORMAT = get_env_variable('LOGGING_FORMAT', '[%(asctime)s.%(msecs)03d][%(levelname)s][%(name)s][%(message)s]')
LOGGING_DATEFMT = get_env_variable('LOGGING_DATEFMT', '%Y-%m-%d %H:%M:%S')

# Application URLs and Endpoints
WATSH_LOGO_URL = get_env_variable('WATSH_LOGO_URL', required=True)
WATSH_LANDING_URL = get_env_variable('WATSH_LANDING_URL', required=True)
WATSH_APP = get_env_variable('WATSH_APP', 'https://app.watsh.io')

# Application Constraints
MIN_SLUG_LEN = int(get_env_variable('MIN_SLUG_LEN', '3'))
MAX_SLUG_LEN = int(get_env_variable('MAX_SLUG_LEN', '36'))
SLUG_REGEX = get_env_variable('SLUG_REGEX', '^[a-z0-9_-]+$')
MAX_DESC_LEN = int(get_env_variable('MAX_DESC_LEN', '200'))
DESC_REGEX = get_env_variable('DESC_REGEX', '^[a-zA-Z0-9_ -]+$')

# External Service Integration
SENTRY_ENABLED = get_env_variable('SENTRY_ENABLED', 'false').lower() == 'true'
SENTRY_DSN = get_env_variable('SENTRY_DSN')
README_ENABLED = get_env_variable('README_ENABLED', 'false').lower() == 'true'
README_SECRET = get_env_variable('README_SECRET')

# Domain Configuration
DOMAIN = get_env_variable('DOMAIN', required=True)
