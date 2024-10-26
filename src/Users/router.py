from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.Users.schemas import ParticipantCreate, ParticipantResponse
from src.Users.crud import ParticipantCRUD
from src.Users.manager import user_hash_manager
from db import get_db

router = APIRouter(prefix="/api/clients", tags=["Participants"])


@router.post(
    "/create", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED
)
async def create_participant(
    participant_data: ParticipantCreate, db: AsyncSession = Depends(get_db)
) -> ParticipantResponse:
    """Эндпоинт для регистрации нового участника."""

    # Проверка уникальности email
    existing_participant = await ParticipantCRUD.get_participant_by_email(
        db, participant_data.email
    )
    if existing_participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email уже используется"
        )

    # Хэширование пароля
    hashed_password = user_hash_manager.hash_password(participant_data.password)

    # Создание участника
    new_participant = await ParticipantCRUD.create_participant(
        db, participant_data, hashed_password
    )
    if not new_participant:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании участника",
        )

    return new_participant
