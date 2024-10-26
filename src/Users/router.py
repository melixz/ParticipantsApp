from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from src.Users.schemas import ParticipantCreate, ParticipantResponse
from src.Users.crud import ParticipantCRUD
from src.Users.manager import user_hash_manager
from src.utils.image_processing import add_watermark
from db import get_db
from io import BytesIO

router = APIRouter(prefix="/api/clients", tags=["Participants"])


@router.post(
    "/create", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED
)
async def create_participant(
    gender: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    avatar: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Эндпоинт для регистрации нового участника с обработкой аватарки."""

    # Проверка уникальности email
    existing_participant = await ParticipantCRUD.get_participant_by_email(db, email)
    if existing_participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email уже используется"
        )

    # Хэширование пароля
    hashed_password = user_hash_manager.hash_password(password)

    # Асинхронная обработка аватарки с наложением водяного знака
    avatar_content = await avatar.read()
    avatar_with_watermark = await add_watermark(BytesIO(avatar_content))

    # Сохранение аватарки в виде строки байтов для базы данных
    avatar_with_watermark.seek(0)
    avatar_bytes = avatar_with_watermark.read()

    # Создание участника
    participant_data = ParticipantCreate(
        gender=gender,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
    )
    new_participant = await ParticipantCRUD.create_participant(
        db, participant_data, hashed_password, avatar=avatar_bytes
    )
    if not new_participant:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании участника",
        )

    # Возвращаем участника с кодированием аватара в Base64
    return ParticipantResponse.from_orm_with_avatar(new_participant)
