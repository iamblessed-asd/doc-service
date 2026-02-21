"""init

Revision ID: 001
Revises: 
Create Date: 2025-02-21 09:31:12.205081

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('content', sa.JSON(), nullable=True),
        sa.Column('owner', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    op.create_index(op.f('ix_documents_owner'), 'documents', ['owner'], unique=False)
    op.create_index(op.f('ix_documents_title'), 'documents', ['title'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_documents_title'), table_name='documents')
    op.drop_index(op.f('ix_documents_owner'), table_name='documents')
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents')