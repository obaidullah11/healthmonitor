from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import time
import os

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

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

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

# Root endpoint - serve frontend
@app.get("/", response_class=HTMLResponse)
async def root():
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return {
            "message": "Health Monitoring System API",
            "version": Config.API_VERSION,
            "docs": "/docs",
            "health_check": "/api/v1/health"
        }

# Frontend route
@app.get("/app", response_class=HTMLResponse)
async def frontend_app():
    """Serve the main frontend application"""
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Frontend not found")

# Serve CSS file
@app.get("/styles.css")
async def get_css():
    """Serve the CSS file"""
    try:
        return FileResponse("frontend/styles.css", media_type="text/css")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="CSS file not found")

# Serve JavaScript file
@app.get("/script.js")
async def get_js():
    """Serve the JavaScript file"""
    try:
        return FileResponse("frontend/script.js", media_type="application/javascript")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="JavaScript file not found")

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






