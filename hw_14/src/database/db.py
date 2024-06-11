from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://postgres:pass@localhost:5432/rest_app"
engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


# Dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
