import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.assistant import router as assistant_router
from app.api.products import router as products_router
from app.core.logging_config import configure_logging


configure_logging()

logger = logging.getLogger(__name__)


from contextlib import asynccontextmanager
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from app.db.base import Base
        from app.db.session import engine
        Base.metadata.create_all(bind=engine)
        from scripts.seed_products import seed_products
        seed_products()
    except Exception as exc:
        logger.warning("Startup DB initialization notice: %s", exc)
    yield


app = FastAPI(
    title="AI E-Commerce Shopping Assistant",
    description="AI-powered shopping and product recommendation assistant.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)
app.include_router(assistant_router)

frontend_dir = Path(__file__).resolve().parents[1] / "frontend"
if frontend_dir.exists():
    app.mount("/demo", StaticFiles(directory=str(frontend_dir), html=True), name="demo")


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unhandled application error: %s %s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
        },
    )


from fastapi.responses import JSONResponse, RedirectResponse


@app.get("/")
def root(request: Request):
    logger.info("Root endpoint requested")
    accept = request.headers.get("accept", "")
    if "text/html" in accept and "application/json" not in accept:
        return RedirectResponse(url="/demo/")

    return {
        "message": "AI E-Commerce Shopping Assistant API",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    logger.info("Health check requested")

    return {
        "status": "healthy"
    }