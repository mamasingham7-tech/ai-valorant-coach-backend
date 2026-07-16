import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.middleware import RequestLoggingMiddleware, setup_exception_handlers
from app.core.audit import setup_audit_listeners
from app.core.redis import redis_client
from app.database.database import engine, get_db_session
from app.modules.users.presentation.api.routes import router as users_router
from app.modules.matches.presentation.api.routes import router as matches_router
from app.modules.live_coaching.presentation.api.routes import router as live_coaching_router

from app.modules.autonomous.presentation.api.routes import router as autonomous_router
from app.modules.federation.presentation.api.routes import router as federation_router
from app.modules.enterprise.presentation.api.routes import router as enterprise_router
from app.modules.player_portal.presentation.api.routes import router as portal_router

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    setup_audit_listeners()
    
    logger.info("Initializing AI Valorant Coach Backend Service", environment=settings.ENVIRONMENT)
    
    # Warn if JWT_SECRET is weak but don't crash — the config has a strong default
    if not settings.JWT_SECRET or len(settings.JWT_SECRET) < 32:
        logger.warning(
            "JWT_SECRET is short. Using built-in dev default. Set a strong secret in production.",
            jwt_len=len(settings.JWT_SECRET)
        )
        
    yield
    
    logger.info("De-initializing backend engine connection pools")
    await engine.dispose()

app = FastAPI(
    title="AI Valorant Coach Backend",
    description="Scalable, Production-Ready Backend for AI-powered Valorant coaching, performance analysis, and insights.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

@app.get("/", status_code=status.HTTP_200_OK, tags=["Monitoring"])
async def root():
    return {
        "name": "AI Valorant Coach Backend",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health/liveness"
    }

# Apply global middlewares
app.add_middleware(RequestLoggingMiddleware)
setup_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://aicoa.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount endpoints
app.include_router(users_router, prefix="/api/v1", tags=["Authentication & Profile"])
app.include_router(matches_router, prefix="/api/v1", tags=["Matches & Telemetry"])
app.include_router(live_coaching_router, prefix="/api/v1", tags=["Live Coaching & Real-time Platform"])

app.include_router(autonomous_router, prefix="/api/v1", tags=["Autonomous AI Coaching"])
app.include_router(federation_router, prefix="/api/v1", tags=["Federated Learning & Platform Marketplace"])
app.include_router(enterprise_router, prefix="/api/v1", tags=["Enterprise Platform & SaaS Portals"])
app.include_router(portal_router, prefix="/api/v1", tags=["Player Portal & Riot Account"])

# Mount prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/health/liveness", status_code=status.HTTP_200_OK, tags=["Monitoring"])
async def liveness():
    """Liveness probe to confirm the server is running."""
    return {"status": "healthy"}

@app.get("/health/startup", status_code=status.HTTP_200_OK, tags=["Monitoring"])
async def startup():
    """Startup probe confirming the service configuration loaded successfully."""
    return {"status": "started", "version": "1.0.0"}

@app.get("/health/readiness", status_code=status.HTTP_200_OK, tags=["Monitoring"])
async def readiness_check(session: AsyncSession = Depends(get_db_session)):
    """Readiness probe checking database pool connectivity."""
    db_ok = True
    redis_ok = redis_client.ping() if redis_client.is_connected else True  # fallback is OK

    try:
        await session.execute(text("SELECT 1"))
    except Exception as e:
        logger.error("Healthcheck Readiness: Database connection failed", error=str(e))
        db_ok = False

    overall_status = "healthy" if db_ok else "unhealthy"
    status_code = status.HTTP_200_OK if db_ok else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "status": overall_status,
            "mode": "sqlite" if settings.USE_SQLITE else "postgres",
            "checks": {
                "database": "healthy" if db_ok else "unhealthy",
                "redis": "in-memory-fallback" if not redis_client.is_connected else "healthy",
            }
        }
        
    )
