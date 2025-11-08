"""create rbac and audit tables

Revision ID: 0001_rbac_audit
Revises: 
Create Date: 2025-11-08 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_rbac_audit'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Roles table
    op.create_table(
        'roles',
        sa.Column('id', postgresql.UUID(as_uuid=True),
                  primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, unique=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
    )

    # Permissions table
    op.create_table(
        'permissions',
        sa.Column('id', postgresql.UUID(as_uuid=True),
                  primary_key=True, nullable=False),
        sa.Column('code', sa.String(length=150), nullable=False, unique=True),
        sa.Column('description', sa.String(length=255)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
    )

    # Role-Permissions association
    op.create_table(
        'role_permissions',
        sa.Column('role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey(
            'roles.id', ondelete='CASCADE'), primary_key=True, nullable=False),
        sa.Column('permission_id', postgresql.UUID(as_uuid=True), sa.ForeignKey(
            'permissions.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    )

    # User-Roles association
    op.create_table(
        'user_roles',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey(
            'users.id', ondelete='CASCADE'), primary_key=True, nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey(
            'roles.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    )

    # Audit logs
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True),
                  primary_key=True, nullable=False),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.String(length=100)),
        sa.Column('before_json', sa.Text()),
        sa.Column('after_json', sa.Text()),
        sa.Column('ip', sa.String(length=100)),
        sa.Column('user_agent', sa.String(length=500)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
    )


def downgrade():
    op.drop_table('audit_logs')
    op.drop_table('user_roles')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
    op.drop_table('roles')
