"""
LegalAId — FastAPI application entry point.
Implements standardized request correlation IDs, CORS protection, and error envelopes.
"""

import uuid
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import init_db, get_connection
from app.api.routes.health import router as health_router
from app.api.routes.cases import router as cases_router
from app.api.routes.legal import router as legal_router
from app.api.routes.documents import router as documents_router
from app.api.routes.analysis import router as analysis_router
from app.api.routes.admin import router as admin_router
from corpus.loader import load_all, STATUTES_DIR

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables and triggers, and auto-seed statutes if database is empty."""
    init_db()
    conn = get_connection()
    try:
        count = conn.execute("SELECT COUNT(*) FROM acts").fetchone()[0]
        if count == 0 and STATUTES_DIR.exists():
            print("[startup] Auto-seeding statute database...")
            load_all(conn, statutes_dir=STATUTES_DIR)
    finally:
        conn.close()
    yield

app = FastAPI(
    title="LegalAId API",
    description=(
        "Production-quality backend engine for LegalAId — AI Legal Rights Assistant for India. "
        "Retrieval-Grounded: every citation is strictly checked against real statutory text."
    ),
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware setup — strict origins (Part 30).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Attach unique request correlation ID to request state and response headers."""
    req_id = request.headers.get("X-Request-ID") or f"req-{uuid.uuid4().hex[:12]}"
    request.state.request_id = req_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    return response


@app.get("/", summary="Root API Endpoint")
def root_endpoint():
    return {
        "application": "LegalAId",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health/ready"
    }


# Standardized Error Handling with Request Correlation ID
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    req_id = getattr(request.state, "request_id", "req-unknown")
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail:
        code = detail["code"]
        message = detail["message"]
    else:
        code = "BAD_REQUEST" if exc.status_code < 500 else "INTERNAL_SERVER_ERROR"
        message = str(detail)

    return JSONResponse(
        status_code=exc.status_code,
        headers={"X-Request-ID": req_id},
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "request_id": req_id
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    req_id = getattr(request.state, "request_id", "req-unknown")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        headers={"X-Request-ID": req_id},
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": str(exc.errors()),
                "request_id": req_id
            }
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", "req-unknown")
    if settings.is_production:
        message = "An unexpected error occurred. Please try again."
    else:
        message = str(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers={"X-Request-ID": req_id},
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": message,
                "request_id": req_id
            }
        }
    )


from app.api.corpus import router as corpus_router

# Register Routers
app.include_router(health_router)
app.include_router(cases_router)
app.include_router(legal_router)
app.include_router(documents_router)
app.include_router(analysis_router)
app.include_router(admin_router)
app.include_router(corpus_router, prefix="/api")
