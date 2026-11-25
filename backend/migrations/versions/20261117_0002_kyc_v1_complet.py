"""KYC V1 complet : parcours, couverture, tentatives, contrôles, événements, webhooks, facturation, identités OIDC.

Les tables kyc_cases et kyc_documents de la première version (données de démonstration) sont remplacées.

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-17 05:23:26.523795

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table('kyc_documents')
    op.drop_table('kyc_cases')
    op.create_table('kyc_journeys',
    sa.Column('organization_id', sa.Uuid(), nullable=True),
    sa.Column('code', sa.String(length=40), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_default', sa.Boolean(), nullable=False),
    sa.Column('required_checks', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('max_attempts', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('expiry_hours', sa.Integer(), nullable=False),
    sa.Column('auto_decision_enabled', sa.Boolean(), nullable=False),
    sa.Column('review_team', sa.String(length=10), nullable=False),
    sa.Column('thresholds', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('decision_rules', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('billing', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('parameters_validated', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_kyc_journeys_organization_id_organizations'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_kyc_journeys')),
    sa.UniqueConstraint('organization_id', 'code', name='uq_kyc_journeys_org_code')
    )
    op.create_index(op.f('ix_kyc_journeys_organization_id'), 'kyc_journeys', ['organization_id'], unique=False)
    op.create_table('webhook_endpoints',
    sa.Column('organization_id', sa.Uuid(), nullable=False),
    sa.Column('url', sa.String(length=500), nullable=False),
    sa.Column('description', sa.String(length=120), nullable=True),
    sa.Column('secret', sa.Text(), nullable=False),
    sa.Column('events', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_webhook_endpoints_organization_id_organizations'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_webhook_endpoints'))
    )
    op.create_index(op.f('ix_webhook_endpoints_organization_id'), 'webhook_endpoints', ['organization_id'], unique=False)
    op.create_table('kyc_cases',
    sa.Column('organization_id', sa.Uuid(), nullable=False),
    sa.Column('journey_id', sa.Uuid(), nullable=False),
    sa.Column('reference', sa.String(length=64), nullable=True),
    sa.Column('country_code', sa.String(length=2), nullable=False),
    sa.Column('document_type', sa.String(length=32), nullable=False),
    sa.Column('language', sa.String(length=2), nullable=False),
    sa.Column('status', sa.Enum('created', 'in_progress', 'action_required', 'processing', 'manual_review', 'verified', 'not_verified', 'failed', 'expired', name='case_status', native_enum=False, length=16), nullable=False),
    sa.Column('status_reason', sa.String(length=48), nullable=True),
    sa.Column('failure_kind', sa.String(length=16), nullable=True),
    sa.Column('risk_level', sa.Enum('low', 'medium', 'high', name='risk_level', native_enum=False, length=8), nullable=True),
    sa.Column('ocr_confidence', sa.Float(), nullable=True),
    sa.Column('flags', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('declared_identity', sa.Text(), nullable=True),
    sa.Column('extracted_data', sa.Text(), nullable=True),
    sa.Column('consent', sa.Text(), nullable=True),
    sa.Column('identity_fingerprint', sa.String(length=64), nullable=True),
    sa.Column('session_token_hash', sa.String(length=64), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('attempt_grants', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('review_team', sa.String(length=10), nullable=True),
    sa.Column('assigned_to_user_id', sa.Uuid(), nullable=True),
    sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(length=80), nullable=False),
    sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('decided_by_user_id', sa.Uuid(), nullable=True),
    sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('decision_reason', sa.Text(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['assigned_to_user_id'], ['users.id'], name=op.f('fk_kyc_cases_assigned_to_user_id_users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['decided_by_user_id'], ['users.id'], name=op.f('fk_kyc_cases_decided_by_user_id_users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['journey_id'], ['kyc_journeys.id'], name=op.f('fk_kyc_cases_journey_id_kyc_journeys'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_kyc_cases_organization_id_organizations'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_kyc_cases')),
    sa.UniqueConstraint('organization_id', 'reference', name='uq_kyc_cases_org_reference')
    )
    op.create_index('ix_kyc_cases_org_fingerprint', 'kyc_cases', ['organization_id', 'identity_fingerprint'], unique=False)
    op.create_index('ix_kyc_cases_org_status_created', 'kyc_cases', ['organization_id', 'status', 'created_at'], unique=False)
    op.create_index('ix_kyc_cases_review_queue', 'kyc_cases', ['status', 'review_team'], unique=False)
    op.create_index(op.f('ix_kyc_cases_session_token_hash'), 'kyc_cases', ['session_token_hash'], unique=True)
    op.create_index('ix_kyc_cases_status_expires', 'kyc_cases', ['status', 'expires_at'], unique=False)
    op.create_table('kyc_document_coverage',
    sa.Column('country_code', sa.String(length=2), nullable=False),
    sa.Column('document_type', sa.String(length=32), nullable=False),
    sa.Column('label_fr', sa.String(length=120), nullable=False),
    sa.Column('label_en', sa.String(length=120), nullable=False),
    sa.Column('sides_required', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('status', sa.String(length=12), nullable=False),
    sa.Column('validated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('validated_by_user_id', sa.Uuid(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['validated_by_user_id'], ['users.id'], name=op.f('fk_kyc_document_coverage_validated_by_user_id_users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_kyc_document_coverage')),
    sa.UniqueConstraint('country_code', 'document_type', name='uq_kyc_coverage_country_document')
    )
    op.create_table('user_identities',
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('provider', sa.String(length=20), nullable=False),
    sa.Column('subject', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=254), nullable=True),
    sa.Column('linked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_user_identities_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user_identities')),
    sa.UniqueConstraint('provider', 'subject', name='uq_user_identities_provider_subject')
    )
    op.create_index(op.f('ix_user_identities_user_id'), 'user_identities', ['user_id'], unique=False)
    op.create_table('billing_events',
    sa.Column('organization_id', sa.Uuid(), nullable=False),
    sa.Column('case_id', sa.Uuid(), nullable=False),
    sa.Column('event_type', sa.String(length=24), nullable=False),
    sa.Column('billable', sa.Boolean(), nullable=False),
    sa.Column('units', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['case_id'], ['kyc_cases.id'], name=op.f('fk_billing_events_case_id_kyc_cases'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_billing_events_organization_id_organizations'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_billing_events'))
    )
    op.create_index('ix_billing_events_org_created', 'billing_events', ['organization_id', 'created_at'], unique=False)
    op.create_table('kyc_attempts',
    sa.Column('case_id', sa.Uuid(), nullable=False),
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('kind', sa.String(length=20), nullable=False),
    sa.Column('reason', sa.String(length=48), nullable=True),
    sa.Column('status', sa.String(length=16), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['case_id'], ['kyc_cases.id'], name=op.f('fk_kyc_attempts_case_id_kyc_cases'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_kyc_attempts')),
    sa.UniqueConstraint('case_id', 'number', name='uq_kyc_attempts_case_number')
    )
    op.create_index(op.f('ix_kyc_attempts_case_id'), 'kyc_attempts', ['case_id'], unique=False)
    op.create_table('kyc_events',
    sa.Column('case_id', sa.Uuid(), nullable=False),
    sa.Column('seq', sa.Integer(), nullable=False),
    sa.Column('event_type', sa.String(length=40), nullable=False),
    sa.Column('from_status', sa.String(length=16), nullable=True),
    sa.Column('to_status', sa.String(length=16), nullable=True),
    sa.Column('reason', sa.String(length=48), nullable=True),
    sa.Column('actor_type', sa.String(length=12), nullable=False),
    sa.Column('actor_id', sa.String(length=64), nullable=True),
    sa.Column('details', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['case_id'], ['kyc_cases.id'], name=op.f('fk_kyc_events_case_id_kyc_cases'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_kyc_events'))
    )
    op.create_index('ix_kyc_events_case_seq', 'kyc_events', ['case_id', 'seq'], unique=False)
    op.create_table('webhook_deliveries',
    sa.Column('endpoint_id', sa.Uuid(), nullable=False),
    sa.Column('organization_id', sa.Uuid(), nullable=False),
    sa.Column('case_id', sa.Uuid(), nullable=True),
    sa.Column('event_type', sa.String(length=40), nullable=False),
    sa.Column('payload', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('status', sa.String(length=12), nullable=False),
    sa.Column('attempts', sa.Integer(), nullable=False),
    sa.Column('last_status_code', sa.Integer(), nullable=True),
    sa.Column('last_error', sa.String(length=200), nullable=True),
    sa.Column('next_attempt_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['case_id'], ['kyc_cases.id'], name=op.f('fk_webhook_deliveries_case_id_kyc_cases'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['endpoint_id'], ['webhook_endpoints.id'], name=op.f('fk_webhook_deliveries_endpoint_id_webhook_endpoints'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_webhook_deliveries_organization_id_organizations'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_webhook_deliveries'))
    )
    op.create_index('ix_webhook_deliveries_due', 'webhook_deliveries', ['status', 'next_attempt_at'], unique=False)
    op.create_index(op.f('ix_webhook_deliveries_endpoint_id'), 'webhook_deliveries', ['endpoint_id'], unique=False)
    op.create_table('kyc_checks',
    sa.Column('case_id', sa.Uuid(), nullable=False),
    sa.Column('attempt_id', sa.Uuid(), nullable=True),
    sa.Column('seq', sa.Integer(), nullable=False),
    sa.Column('check_type', sa.String(length=24), nullable=False),
    sa.Column('status', sa.String(length=12), nullable=False),
    sa.Column('is_required', sa.Boolean(), nullable=False),
    sa.Column('details', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('engine', sa.String(length=40), nullable=True),
    sa.Column('version', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['attempt_id'], ['kyc_attempts.id'], name=op.f('fk_kyc_checks_attempt_id_kyc_attempts'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['case_id'], ['kyc_cases.id'], name=op.f('fk_kyc_checks_case_id_kyc_cases'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_kyc_checks'))
    )
    op.create_index('ix_kyc_checks_case_type', 'kyc_checks', ['case_id', 'check_type'], unique=False)
    op.create_table('kyc_documents',
    sa.Column('case_id', sa.Uuid(), nullable=False),
    sa.Column('attempt_id', sa.Uuid(), nullable=False),
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
    sa.ForeignKeyConstraint(['attempt_id'], ['kyc_attempts.id'], name=op.f('fk_kyc_documents_attempt_id_kyc_attempts'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['case_id'], ['kyc_cases.id'], name=op.f('fk_kyc_documents_case_id_kyc_cases'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_kyc_documents_organization_id_organizations'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_kyc_documents')),
    sa.UniqueConstraint('attempt_id', 'side', name='uq_kyc_documents_attempt_side')
    )
    op.create_index(op.f('ix_kyc_documents_case_id'), 'kyc_documents', ['case_id'], unique=False)
    op.create_index('ix_kyc_documents_org_sha256', 'kyc_documents', ['organization_id', 'sha256'], unique=False)
    op.alter_column('users', 'password_hash',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)

    journeys = sa.table(
        'kyc_journeys',
        sa.column('id', sa.Uuid()), sa.column('organization_id', sa.Uuid()), sa.column('code', sa.String()), sa.column('name', sa.String()),
        sa.column('is_active', sa.Boolean()), sa.column('is_default', sa.Boolean()), sa.column('required_checks', sa.JSON()),
        sa.column('max_attempts', sa.JSON()), sa.column('expiry_hours', sa.Integer()), sa.column('auto_decision_enabled', sa.Boolean()),
        sa.column('review_team', sa.String()), sa.column('thresholds', sa.JSON()), sa.column('decision_rules', sa.JSON()),
        sa.column('billing', sa.JSON()), sa.column('parameters_validated', sa.Boolean()),
    )
    op.bulk_insert(journeys, [{
        'id': uuid.uuid4(), 'organization_id': None, 'code': 'standard', 'name': 'Parcours KYC standard', 'is_active': True, 'is_default': True,
        'required_checks': ['document_quality', 'document_recognition', 'ocr_extraction', 'declared_match'],
        'max_attempts': {'recapture': 3, 'data_correction': 2, 'technical_retry': 3}, 'expiry_hours': 72, 'auto_decision_enabled': False,
        'review_team': 'either', 'thresholds': {'ocr_review': 0.9, 'name_match': 0.9, 'name_partial': 0.75},
        'decision_rules': {'declared_mismatch': 'manual_review', 'declared_partial': 'manual_review', 'expired_document': 'manual_review',
                           'underage': 'not_verified', 'duplicate_image': 'manual_review', 'duplicate_identity': 'manual_review',
                           'low_confidence': 'manual_review', 'biometric_failure': 'manual_review'},
        'billing': {'case_created': True, 'attempts': False, 'manual_review': False, 'extra_checks': False},
        'parameters_validated': False,
    }])
    coverage = sa.table(
        'kyc_document_coverage',
        sa.column('id', sa.Uuid()), sa.column('country_code', sa.String()), sa.column('document_type', sa.String()),
        sa.column('label_fr', sa.String()), sa.column('label_en', sa.String()), sa.column('sides_required', sa.JSON()),
        sa.column('status', sa.String()), sa.column('notes', sa.Text()),
    )
    op.bulk_insert(coverage, [{
        'id': uuid.uuid4(), 'country_code': 'CM', 'document_type': 'cni_cm', 'label_fr': "Carte nationale d'identité (Cameroun)",
        'label_en': 'National identity card (Cameroon)', 'sides_required': ['front'], 'status': 'testing',
        'notes': "Recto lu par PaddleOCR ; à valider sur un jeu de test représentatif avant passage en « supported ».",
    }])


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("UPDATE users SET password_hash = '!' WHERE password_hash IS NULL")
    op.alter_column('users', 'password_hash',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.drop_index('ix_kyc_documents_org_sha256', table_name='kyc_documents')
    op.drop_index(op.f('ix_kyc_documents_case_id'), table_name='kyc_documents')
    op.drop_table('kyc_documents')
    op.drop_index('ix_kyc_checks_case_type', table_name='kyc_checks')
    op.drop_table('kyc_checks')
    op.drop_index(op.f('ix_webhook_deliveries_endpoint_id'), table_name='webhook_deliveries')
    op.drop_index('ix_webhook_deliveries_due', table_name='webhook_deliveries')
    op.drop_table('webhook_deliveries')
    op.drop_index('ix_kyc_events_case_seq', table_name='kyc_events')
    op.drop_table('kyc_events')
    op.drop_index(op.f('ix_kyc_attempts_case_id'), table_name='kyc_attempts')
    op.drop_table('kyc_attempts')
    op.drop_index('ix_billing_events_org_created', table_name='billing_events')
    op.drop_table('billing_events')
    op.drop_index(op.f('ix_user_identities_user_id'), table_name='user_identities')
    op.drop_table('user_identities')
    op.drop_table('kyc_document_coverage')
    op.drop_index('ix_kyc_cases_status_expires', table_name='kyc_cases')
    op.drop_index(op.f('ix_kyc_cases_session_token_hash'), table_name='kyc_cases')
    op.drop_index('ix_kyc_cases_review_queue', table_name='kyc_cases')
    op.drop_index('ix_kyc_cases_org_status_created', table_name='kyc_cases')
    op.drop_index('ix_kyc_cases_org_fingerprint', table_name='kyc_cases')
    op.drop_table('kyc_cases')
    op.drop_index(op.f('ix_webhook_endpoints_organization_id'), table_name='webhook_endpoints')
    op.drop_table('webhook_endpoints')
    op.drop_index(op.f('ix_kyc_journeys_organization_id'), table_name='kyc_journeys')
    op.drop_table('kyc_journeys')
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

