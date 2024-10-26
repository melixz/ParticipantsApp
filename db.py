from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Настройка строки подключения к базе данных
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

# Создаем асинхронный движок базы данных
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаем базовый класс для моделей
Base = declarative_base()

# Создаем фабрику сессий
async_session = sessionmaker(
    bind=engine, autocommit=False, autoflush=False, class_=AsyncSession
)


async def get_db():
    """Получение сессии базы данных."""
    session = async_session()
    try:
        yield session
    finally:
        await session.close()
