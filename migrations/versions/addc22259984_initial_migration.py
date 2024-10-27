"""Initial migration

Revision ID: addc22259984
Revises: 
Create Date: 2024-10-27 16:57:24.121161

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'addc22259984'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('participants',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('avatar', sa.LargeBinary(), nullable=True),
    sa.Column('gender', sa.String(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('longitude', sa.String(), nullable=True),
    sa.Column('latitude', sa.String(), nullable=True),
    sa.Column('city', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_participants_email'), 'participants', ['email'], unique=True)
    op.create_index(op.f('ix_participants_id'), 'participants', ['id'], unique=False)
    op.create_table('matches',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('target_user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['target_user_id'], ['participants.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['participants.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'target_user_id', name='unique_match')
    )
    op.create_index(op.f('ix_matches_id'), 'matches', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_matches_id'), table_name='matches')
    op.drop_table('matches')
    op.drop_index(op.f('ix_participants_id'), table_name='participants')
    op.drop_index(op.f('ix_participants_email'), table_name='participants')
    op.drop_table('participants')
    # ### end Alembic commands ###
