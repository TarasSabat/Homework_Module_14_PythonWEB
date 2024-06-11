import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException
from fastapi_limiter import FastAPILimiter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware

from src.conf.config import config
from src.database.db import get_db
from src.routes import contacts, auth, users

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are needed by your app,
    like connecting to databases or initializing caches.

    :return: A coroutine, which is a function that returns a future
    :doc-author: Trelent
    """
    r = await redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
    )
    await FastAPILimiter.init(r)


@app.get("/")
def read_root():
    """
    The read_root function returns a dictionary with the key &quot;message&quot; and value &quot;Hello World !&quot;.

    :return: A dictionary with a &quot;message&quot; key
    :doc-author: Trelent
    """
    return {"message": "Hello World !"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    The healthchecker function is a simple function that checks if the database is up and running.
    It does this by making a request to the database, which will raise an exception if it's not working.

    :param db: AsyncSession: Get the database session
    :return: A dict with a message
    :doc-author: Trelent
    """
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
