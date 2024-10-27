from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Participant, Match
from .schemas import ParticipantCreate
from typing import Optional, List
from datetime import datetime, timedelta
from src.utils.logging import AppLogger
from src.utils.distance import calculate_distance
from functools import lru_cache


logger = AppLogger().get_logger()

# Устанавливаем время жизни кэша (7 дней в секундах)
CACHE_TTL = 7 * 24 * 60 * 60


class ParticipantCRUD:
    @staticmethod
    async def get_participant_by_email(
        db: AsyncSession, email: str
    ) -> Optional[Participant]:
        """Получение участника по email."""
        result = await db.execute(select(Participant).filter_by(email=email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_participant_by_id(
        db: AsyncSession, participant_id: int
    ) -> Optional[Participant]:
        """Получение участника по ID."""
        result = await db.execute(
            select(Participant).where(Participant.id == participant_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_participant(
        db: AsyncSession,
        participant_data: ParticipantCreate,
        hashed_password: str,
        avatar: bytes,
        latitude: Optional[str] = None,
        longitude: Optional[str] = None,
        city: Optional[str] = None,  # Добавлено поле city
    ) -> Optional[Participant | bool]:
        """Создание нового участника с хэшированным паролем, аватаркой и координатами."""
        new_participant = Participant(
            avatar=avatar,
            gender=participant_data.gender,
            first_name=participant_data.first_name,
            last_name=participant_data.last_name,
            email=participant_data.email,
            hashed_password=hashed_password,
            latitude=latitude,
            longitude=longitude,
            city=city,  # Сохранение города в базе данных
        )

        try:
            db.add(new_participant)
            await db.commit()
            await db.refresh(new_participant)
            return new_participant
        except Exception as e:
            await db.rollback()
            logger.error("Ошибка при создании участника: %s", e)
            return False

    @staticmethod
    async def get_participants(
        db: AsyncSession,
        gender: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> List[Participant]:
        """Получение списка участников с фильтрацией по полу, имени и фамилии."""
        query = select(Participant)
        if gender:
            query = query.where(Participant.gender == gender)
        if first_name:
            query = query.where(Participant.first_name.ilike(f"%{first_name}%"))
        if last_name:
            query = query.where(Participant.last_name.ilike(f"%{last_name}%"))

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    @lru_cache(maxsize=1024)
    async def get_nearby_participants(
        db: AsyncSession,
        base_lat: float,
        base_lon: float,
        max_distance: float,
        gender: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> List[Participant]:
        """Получает список участников, находящихся в пределах max_distance километров с кэшированием."""
        query = select(Participant)

        if gender:
            query = query.where(Participant.gender == gender)
        if first_name:
            query = query.where(Participant.first_name.ilike(f"%{first_name}%"))
        if last_name:
            query = query.where(Participant.last_name.ilike(f"%{last_name}%"))

        result = await db.execute(query)
        participants = result.scalars().all()

        # Фильтруем участников по расстоянию
        nearby_participants = [
            p
            for p in participants
            if p.latitude
            and p.longitude
            and calculate_distance(
                base_lat, base_lon, float(p.latitude), float(p.longitude)
            )
            <= max_distance
        ]

        return nearby_participants


class MatchCRUD:
    @staticmethod
    async def create_match(
        db: AsyncSession, user_id: int, target_user_id: int
    ) -> Optional[Match]:
        """Создание лайка между участниками. Проверяет, существует ли уже лайк от user_id к target_user_id."""
        existing_match = await db.execute(
            select(Match).where(
                and_(Match.user_id == user_id, Match.target_user_id == target_user_id)
            )
        )
        if existing_match.scalar() is not None:
            raise Exception("Лайк уже существует")

        match = Match(user_id=user_id, target_user_id=target_user_id)
        db.add(match)
        await db.commit()
        return match

    @staticmethod
    async def check_mutual_like(
        db: AsyncSession, user_id: int, target_user_id: int
    ) -> bool:
        """Проверяет, есть ли взаимный лайк между пользователями."""
        result = await db.execute(
            select(Match)
            .where(Match.user_id == target_user_id)
            .where(Match.target_user_id == user_id)
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def get_daily_likes_count(db: AsyncSession, user_id: int) -> int:
        """Возвращает количество лайков, поставленных участником за последние 24 часа."""
        day_ago = datetime.utcnow() - timedelta(days=1)
        result = await db.execute(
            select(func.count(Match.id))
            .where(Match.user_id == user_id)
            .where(Match.created_at >= day_ago)
        )
        return result.scalar()
