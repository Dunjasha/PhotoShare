from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.routes import auth, users

app = FastAPI(title="Contacts API",
              version="1.0",
              description="A REST API for Photo Share App",
              )

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=origins,
    allow_headers=origins,
)

static_dir = Path("src/static")
if not static_dir.exists():
    static_dir.mkdir(parents=True)

app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")


@app.get("/")
def root():
    """
    Root endpoint that returns a welcome message.

    Returns:
        dict: Simple welcome message
    """
    return {"message": "Photo Share Application"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Check the health of the application and database connection.

    Args:
        db (AsyncSession): Database session dependency

    Returns:
        dict: Success message if healthy

    Raises:
        HTTPException: 500 if database connection fails
    """
    try:
        result = await db.execute(text("SELECT 1"))
        if not result.fetchone():
            raise HTTPException(status_code=500, detail="Database misconfigured")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="DB connection error")
