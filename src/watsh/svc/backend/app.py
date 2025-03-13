from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from .handlers import exception_handlers
from .config import MIDDLEWARE_SESSION_SECRET, VERSION, DOMAIN
from .client import setup_indexes, close_client

from .routers.me import router as router_me
from .routers.auth import router as router_auth
from .routers.health import router as router_health
from .routers.token import router as router_token
from .routers.project import router as router_project
from .routers.member import router as router_member
from .routers.ownership import router as router_ownership
from .routers.environment import router as router_environment
from .routers.branch import router as router_branch
from .routers.item import router as router_item
from .routers.commit import router as router_commit
from .routers.schema import router as router_schema
from .routers.json_value import router as router_json
from .routers.items import router as router_items
from .routers.webhook import router as router_webhook
from .routers.ws import router as router_ws


summary="Configuration Management by API"
description = """Watsh is configuration management platform letting developers automate and test application configurations."""

app = FastAPI(
    title="Watsh Back-End Server",
    summary=summary,
    description=description,
    version=VERSION,
    terms_of_service="http://www.watsh.io/terms-of-service",
    servers=[
        {"url": DOMAIN, "description": "Watsh API Server"}
    ],
    contact={
        "name": "Watsh",
        "email": "contact@watsh.io",
    },
    exception_handlers=exception_handlers
)

# Middlewares
app.add_middleware(SessionMiddleware, secret_key=MIDDLEWARE_SESSION_SECRET)

# Routers
app.include_router(router_me, prefix="/v1")
app.include_router(router_auth, prefix="/v1")
app.include_router(router_health, prefix="/v1")
app.include_router(router_token, prefix="/v1")
app.include_router(router_project, prefix="/v1")
app.include_router(router_member, prefix="/v1")
app.include_router(router_ownership, prefix="/v1")
app.include_router(router_environment, prefix="/v1")
app.include_router(router_branch, prefix="/v1")
app.include_router(router_item, prefix="/v1")
app.include_router(router_commit, prefix="/v1")
app.include_router(router_schema, prefix="/v1")
app.include_router(router_json, prefix="/v1")
app.include_router(router_items, prefix="/v1")
app.include_router(router_webhook, prefix="/v1")
app.include_router(router_ws, prefix="/v1")

# Event handlers
app.add_event_handler("startup", setup_indexes)
app.add_event_handler("shutdown", close_client)