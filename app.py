from fastapi import FastAPI
from src.Users.router import router as participant_router
from db import engine, Base
import uvicorn

app = FastAPI(title="ParticipantsApp", version="1.0")

# Подключаем роутеры
app.include_router(participant_router)


# Инициализация базы данных
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        # Создаем таблицы при запуске приложения, если они еще не существуют
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def on_shutdown():
    # Здесь можно добавить код для завершения соединений и очистки ресурсов при выключении приложения
    pass


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
