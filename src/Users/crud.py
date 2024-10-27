from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Participant, Match
from .schemas import ParticipantCreate
from typing import Optional
from datetime import datetime, timedelta
from src.utils.logging import AppLogger

logger = AppLogger().get_logger()


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
    ) -> Optional[Participant | bool]:
        """Создание нового участника с хэшированным паролем и аватаркой."""
        new_participant = Participant(
            avatar=avatar,
            gender=participant_data.gender,
            first_name=participant_data.first_name,
            last_name=participant_data.last_name,
            email=participant_data.email,
            hashed_password=hashed_password,
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


class MatchCRUD:
    @staticmethod
    async def create_match(
        db: AsyncSession, user_id: int, target_user_id: int
    ) -> Optional[Match]:
        # Проверяем, существует ли уже лайк
        existing_match = await db.execute(
            select(Match).where(
                and_(Match.user_id == user_id, Match.target_user_id == target_user_id)
            )
        )
        if existing_match.scalar() is not None:
            raise Exception("Лайк уже существует")

        # Создаем лайк
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
