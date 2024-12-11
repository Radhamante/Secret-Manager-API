import logging
import os

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.database import create_tables
from app.routers.auth import auth_router
from app.routers.secret import secrets_router
from app.routers.secretLogs import secrets_log_router
from app.utils import PrometheusMiddleware, metrics, setting_otlp

logger = logging.getLogger(__name__)

app = FastAPI()

OTLP_GRPC_ENDPOINT = os.environ.get("OTLP_GRPC_ENDPOINT", "http://tempo:4317")
APP_NAME = os.environ.get("APP_NAME", "fastapi-app")

class EndpointFilter(logging.Filter):
    # Uvicorn endpoint access log filter
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("GET /metrics") == -1


# Filter out /endpoint
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())


# Setting metrics middleware
app.add_middleware(PrometheusMiddleware, app_name=APP_NAME)
app.add_route("/metrics", metrics)

# Setting OpenTelemetry exporter
setting_otlp(app, APP_NAME, OTLP_GRPC_ENDPOINT)

app.include_router(auth_router)
app.include_router(secrets_router)
app.include_router(secrets_log_router)


@app.on_event("startup")
async def onStartup():
    create_tables()


@app.get("/", include_in_schema=False)
def redirectToStatic():
    return RedirectResponse(url="/docs")
