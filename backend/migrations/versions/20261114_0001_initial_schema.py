"""Schéma initial : organisations, utilisateurs, clés API, dossiers KYC, documents, audit.

Revision ID: 0001
Revises: 
Create Date: 2026-11-14 08:28:10.657925

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('organizations',
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('slug', sa.String(length=50), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('enabled_modules', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_organizations'))
    )
    op.create_index(op.f('ix_organizations_slug'), 'organizations', ['slug'], unique=True)
    op.create_table('audit_logs',
    sa.Column('organization_id', sa.Uuid(), nullable=True),
    sa.Column('actor_type', sa.Enum('user', 'api_key', 'system', name='actor_type', native_enum=False, length=12), nullable=False),
    sa.Column('actor_id', sa.String(length=64), nullable=True),
    sa.Column('action', sa.String(length=64), nullable=False),
    sa.Column('resource_type', sa.String(length=32), nullable=False),
    sa.Column('resource_id', sa.String(length=64), nullable=True),
    sa.Column('ip_address', sa.String(length=45), nullable=True),
    sa.Column('request_id', sa.String(length=64), nullable=True),
    sa.Column('details', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_audit_logs_organization_id_organizations'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_audit_logs'))
    )
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)
    op.create_index('ix_audit_logs_org_created', 'audit_logs', ['organization_id', 'created_at'], unique=False)
    op.create_index('ix_audit_logs_resource', 'audit_logs', ['resource_type', 'resource_id'], unique=False)
    op.create_table('users',
    sa.Column('organization_id', sa.Uuid(), nullable=True),
    sa.Column('email', sa.String(length=254), nullable=False),
    sa.Column('full_name', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('role', sa.Enum('super_admin', 'admin', 'reviewer', 'viewer', 'integration', name='user_role', native_enum=False, length=20), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('failed_login_attempts', sa.Integer(), nullable=False),
    sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_users_organization_id_organizations'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users'))
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_organization_id'), 'users', ['organization_id'], unique=False)
    op.create_table('api_keys',
    sa.Column('organization_id', sa.Uuid(), nullable=False),
    sa.Column('created_by_user_id', sa.Uuid(), nullable=True),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('prefix', sa.String(length=8), nullable=False),
    sa.Column('key_hash', sa.String(length=64), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name=op.f('fk_api_keys_created_by_user_id_users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_api_keys_organization_id_organizations'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_api_keys'))
    )
    op.create_index(op.f('ix_api_keys_organization_id'), 'api_keys', ['organization_id'], unique=False)
    op.create_index(op.f('ix_api_keys_prefix'), 'api_keys', ['prefix'], unique=True)
    op.create_table('kyc_cases',
    sa.Column('organization_id', sa.Uuid(), nullable=False),
    sa.Column('reference', sa.String(length=64), nullable=True),
    sa.Column('document_type', sa.Enum('cni_cm', name='document_type', native_enum=False, length=16), nullable=False),
    sa.Column('status', sa.Enum('processing', 'pending_review', 'approved', 'rejected', 'failed', name='case_status', native_enum=False, length=16), nullable=False),
    sa.Column('risk_level', sa.Enum('low', 'medium', 'high', name='risk_level', native_enum=False, length=8), nullable=True),
    sa.Column('ocr_confidence', sa.Float(), nullable=True),
    sa.Column('extracted_data', sa.Text(), nullable=True),
    sa.Column('flags', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('identity_fingerprint', sa.String(length=64), nullable=True),
    sa.Column('failure_reason', sa.String(length=64), nullable=True),
    sa.Column('created_by', sa.String(length=80), nullable=False),
    sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('decided_by_user_id', sa.Uuid(), nullable=True),
    sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('decision_reason', sa.Text(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['decided_by_user_id'], ['users.id'], name=op.f('fk_kyc_cases_decided_by_user_id_users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_kyc_cases_organization_id_organizations'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_kyc_cases')),
    sa.UniqueConstraint('organization_id', 'reference', name='uq_kyc_cases_org_reference')
    )
    op.create_index('ix_kyc_cases_org_fingerprint', 'kyc_cases', ['organization_id', 'identity_fingerprint'], unique=False)
    op.create_index('ix_kyc_cases_org_status_created', 'kyc_cases', ['organization_id', 'status', 'created_at'], unique=False)
    op.create_table('kyc_documents',
    sa.Column('case_id', sa.Uuid(), nullable=False),
    sa.Column('organization_id', sa.Uuid(), nullable=False),
    sa.Column('side', sa.Enum('front', 'back', name='document_side', native_enum=False, length=8), nullable=False),
    sa.Column('storage_key', sa.String(length=200), nullable=False),
    sa.Column('sha256', sa.String(length=64), nullable=False),
    sa.Column('mime_type', sa.String(length=32), nullable=False),
    sa.Column('size_bytes', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
    sa.Column('width', sa.Integer(), nullable=False),
    sa.Column('height', sa.Integer(), nullable=False),
    sa.Column('sharpness', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['case_id'], ['kyc_cases.id'], name=op.f('fk_kyc_documents_case_id_kyc_cases'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_kyc_documents_organization_id_organizations'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_kyc_documents')),
    sa.UniqueConstraint('case_id', 'side', name='uq_kyc_documents_case_side')
    )
    op.create_index(op.f('ix_kyc_documents_case_id'), 'kyc_documents', ['case_id'], unique=False)
    op.create_index('ix_kyc_documents_org_sha256', 'kyc_documents', ['organization_id', 'sha256'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_kyc_documents_org_sha256', table_name='kyc_documents')
    op.drop_index(op.f('ix_kyc_documents_case_id'), table_name='kyc_documents')
    op.drop_table('kyc_documents')
    op.drop_index('ix_kyc_cases_org_status_created', table_name='kyc_cases')
    op.drop_index('ix_kyc_cases_org_fingerprint', table_name='kyc_cases')
    op.drop_table('kyc_cases')
    op.drop_index(op.f('ix_api_keys_prefix'), table_name='api_keys')
    op.drop_index(op.f('ix_api_keys_organization_id'), table_name='api_keys')
    op.drop_table('api_keys')
    op.drop_index(op.f('ix_users_organization_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index('ix_audit_logs_resource', table_name='audit_logs')
    op.drop_index('ix_audit_logs_org_created', table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index(op.f('ix_organizations_slug'), table_name='organizations')
    op.drop_table('organizations')
