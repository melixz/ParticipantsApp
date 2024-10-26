from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from src.Users.schemas import (
    ParticipantCreate,
    ParticipantResponse,
    MatchRequest,
    MatchResponse,
    GenderEnum,
)
from src.Users.crud import ParticipantCRUD, MatchCRUD
from src.Users.manager import user_hash_manager
from src.utils.image_processing import add_watermark
from db import get_db
from config import settings
from io import BytesIO

router = APIRouter(
    prefix="/api/clients", tags=["Участники"]
)  # Обозначаем название группы как "Участники"


@router.post(
    "/create",
    response_model=ParticipantResponse,
    status_code=status.HTTP_201_CREATED,
    description="Эндпоинт для регистрации нового участника с возможностью загрузки аватарки и указания личных данных",
)
async def create_participant(
    gender: GenderEnum = Form(..., description="Пол участника"),
    first_name: str = Form(..., description="Имя участника"),
    last_name: str = Form(..., description="Фамилия участника"),
    email: str = Form(..., description="Электронная почта участника"),
    password: str = Form(..., description="Пароль для доступа"),
    avatar: UploadFile = File(..., description="Файл аватарки участника"),
    db: AsyncSession = Depends(get_db),
):
    """Эндпоинт для регистрации участника с водяным знаком на аватарке."""
    existing_participant = await ParticipantCRUD.get_participant_by_email(db, email)
    if existing_participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email уже используется"
        )

    hashed_password = user_hash_manager.hash_password(password)

    avatar_content = await avatar.read()
    avatar_with_watermark = await add_watermark(BytesIO(avatar_content))
    avatar_with_watermark.seek(0)
    avatar_bytes = avatar_with_watermark.read()

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

    return ParticipantResponse.from_orm_with_avatar(new_participant)


@router.post(
    "/{id}/match",
    response_model=MatchResponse,
    description="Эндпоинт для оценки другого участника (ставится лайк)",
)
async def match_participant(
    id: int,
    match_request: MatchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Оценка участником другого участника с проверкой на лимит."""
    user_id = match_request.user_id

    daily_likes_count = await MatchCRUD.get_daily_likes_count(db, user_id)
    if daily_likes_count >= settings.MAX_LIKES_PER_DAY:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Лимит лайков на сегодня исчерпан",
        )

    await MatchCRUD.create_match(db, user_id, id)

    if await MatchCRUD.check_mutual_like(db, user_id, id):
        target_participant = await ParticipantCRUD.get_participant_by_id(db, id)
        if target_participant:
            return MatchResponse(
                message=f"Взаимная симпатия с {target_participant.first_name}!",
                email=target_participant.email,
            )
    else:
        return MatchResponse(message="Лайк добавлен, но взаимной симпатии нет.")
