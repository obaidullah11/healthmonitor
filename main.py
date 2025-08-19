from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import time

from config import Config
from app.api.routes import router

# Create FastAPI app
app = FastAPI(
    title=Config.API_TITLE,
    version=Config.API_VERSION,
    description=Config.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["Health Monitoring"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "data": None
        }
    )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Health Monitoring System API",
        "version": Config.API_VERSION,
        "docs": "/docs",
        "health_check": "/api/v1/health"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    print("Starting Health Monitoring System API...")
    print(f"API Documentation: http://{Config.HOST}:{Config.PORT}/docs")
    print(f"Health Check: http://{Config.HOST}:{Config.PORT}/api/v1/health")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down Health Monitoring System API...")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level="info"
    )




