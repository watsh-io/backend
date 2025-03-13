import logging
import uvicorn
import sentry_sdk

from .config import (
    LOGGING_LEVEL, LOGGING_FORMAT, LOGGING_DATEFMT,
    SENTRY_ENABLED, SENTRY_DSN,
    SERVER_HOST, SERVER_PORT, SERVER_PROXY_HEADER, SERVER_RELOAD,
)

def configure_logging() -> None:
    """
    Configure the logging for the application.
    """
    logging.basicConfig(
        level=LOGGING_LEVEL, 
        datefmt=LOGGING_DATEFMT, 
        format=LOGGING_FORMAT
    )

def initialize_sentry() -> None:
    """
    Initialize Sentry SDK for error tracking, if enabled.
    """
    if SENTRY_ENABLED:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            enable_tracing=True,
            traces_sample_rate=1.0,  # Adjust in production as needed
            profiles_sample_rate=1.0,  # Adjust in production as needed
        )

def run_server() -> None:
    """
    Run the Uvicorn server with the specified configuration.
    """
    uvicorn.run(
        'src.watsh.svc.backend.app:app',  # Adjust the import path as needed
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=SERVER_RELOAD,
        proxy_headers=SERVER_PROXY_HEADER,
        forwarded_allow_ips='*',  # Consider restricting in production
    )
