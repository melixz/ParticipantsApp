from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
    Query,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select
from src.Users.schemas import (
    ParticipantCreate,
    ParticipantResponse,
    MatchRequest,
    MatchResponse,
    GenderEnum,
)
from src.Users.crud import ParticipantCRUD, MatchCRUD
from src.Users.manager import user_hash_manager
from src.Users.models import Participant
from src.utils.image_processing import add_watermark
from db import get_db
from config import settings
from io import BytesIO
from typing import Optional, List

router = APIRouter(prefix="/api/clients", tags=["Участники"])


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

    # Формируем URL для аватарки после создания
    avatar_url = f"http://127.0.0.1:8000/api/clients/avatar/{new_participant.id}"

    # Возвращаем результат с аватаркой
    return ParticipantResponse.from_orm_with_avatar(
        new_participant, avatar_url=avatar_url
    )


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

    # Проверка лимита лайков за день
    daily_likes_count = await MatchCRUD.get_daily_likes_count(db, user_id)
    if daily_likes_count >= settings.MAX_LIKES_PER_DAY:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Лимит лайков на сегодня исчерпан",
        )

    try:
        # Пытаемся создать новый лайк
        await MatchCRUD.create_match(db, user_id, id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже поставили лайк",
        )

    # Проверяем, есть ли взаимная симпатия
    if await MatchCRUD.check_mutual_like(db, user_id, id):
        target_participant = await ParticipantCRUD.get_participant_by_id(db, id)
        if target_participant:
            return MatchResponse(
                message=f"Взаимная симпатия с {target_participant.first_name}!",
                email=target_participant.email,
            )
    else:
        return MatchResponse(message="Лайк добавлен, но взаимной симпатии нет.")


@router.get(
    "/list",
    response_model=List[ParticipantResponse],
    description="Эндпоинт для получения списка участников с возможностью фильтрации и сортировки по дате регистрации",
)
async def get_participants(
    gender: Optional[GenderEnum] = Query(None, description="Фильтр по полу"),
    first_name: Optional[str] = Query(None, description="Фильтр по имени"),
    last_name: Optional[str] = Query(None, description="Фильтр по фамилии"),
    sort_by_date: Optional[bool] = Query(
        False, description="Сортировка по дате регистрации (по убыванию)"
    ),
    db: AsyncSession = Depends(get_db),
):
    """Эндпоинт для получения списка участников с фильтрацией и сортировкой."""
    query = select(Participant)

    if gender:
        query = query.filter(Participant.gender == gender)
    if first_name:
        query = query.filter(Participant.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Participant.last_name.ilike(f"%{last_name}%"))
    if sort_by_date:
        query = query.order_by(desc(Participant.created_at))
    else:
        query = query.order_by(Participant.created_at)

    result = await db.execute(query)
    participants = result.scalars().all()

    # Формируем avatar_url для каждого участника
    participants_responses = [
        ParticipantResponse.from_orm_with_avatar(
            participant,
            avatar_url=f"http://127.0.0.1:8000/api/clients/avatar/{participant.id}",
        )
        for participant in participants
    ]

    return participants_responses
