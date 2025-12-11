import sys
import os

# Явно добавляем путь к src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Теперь импорт должен работать
try:
    from config import settings
except ImportError:
    # Альтернативный путь для Docker
    import sys
    sys.path.insert(0, '/app')
    from src.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Импортируем роутеры
try:
    from routes import router
    app.include_router(router, prefix="/api/v1")
except ImportError:
    from src.routes import router
    app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # Используем относительный путь
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )