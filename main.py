"""a2a-mcp — self-hosted MCP gateway.

Expose any Python function as an MCP tool. One deploy, any MCP client.
"""

from contextlib import asynccontextmanager

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import get_settings
from mcp import router as mcp_router
from session import get_tracker
from shared.logging import setup_logging
from ui import router as ui_router

setup_logging()
logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    import skills
    skills.register_all()
    logger.info("a2a-mcp started", redis=bool(settings.REDIS_URL))
    yield
    await get_tracker().close()
    logger.info("a2a-mcp stopped")


app = FastAPI(
    title="a2a-mcp",
    description="Self-hosted MCP gateway — expose any Python function as an MCP tool.",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG_MODE else None,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "a2a-mcp", "version": "0.1.0"}


app.include_router(mcp_router, prefix="/mcp", tags=["mcp"])
app.include_router(ui_router, prefix="/ui", tags=["ui"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.HOT_RELOAD,
        log_config=None,
        access_log=False,
    )
