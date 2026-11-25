"""Extensions plateforme : e-mails, demandes publiques, contenus, accès développeur, facturation, MFA, Sandbox, révocation de sessions.

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-21 13:02:58.384860

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, Sequence[str], None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('billing_plans',
    sa.Column('code', sa.String(length=40), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('description', sa.String(length=400), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('prices', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_billing_plans')),
    sa.UniqueConstraint('code', name=op.f('uq_billing_plans_code'))
    )
    op.create_table('document_counters',
    sa.Column('key', sa.String(length=40), nullable=False),
    sa.Column('value', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('key', name=op.f('pk_document_counters'))
    )
    op.create_table('email_outbox',
    sa.Column('template', sa.String(length=40), nullable=False),
    sa.Column('locale', sa.String(length=2), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=10), nullable=False),
    sa.Column('attempts', sa.Integer(), nullable=False),
    sa.Column('last_error', sa.String(length=200), nullable=True),
    sa.Column('related_id', sa.Uuid(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_email_outbox'))
    )
    op.create_index('ix_email_outbox_due', 'email_outbox', ['status', 'created_at'], unique=False)
    op.create_table('subscriptions',
    sa.Column('organization_id', sa.Uuid(), nullable=False),
    sa.Column('plan_id', sa.Uuid(), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('status', sa.String(length=10), nullable=False),
    sa.Column('tax_rate', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.Column('started_at', sa.Date(), nullable=False),
    sa.Column('ended_at', sa.Date(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_subscriptions_organization_id_organizations'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['plan_id'], ['billing_plans.id'], name=op.f('fk_subscriptions_plan_id_billing_plans'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_subscriptions'))
    )
    op.create_index(op.f('ix_subscriptions_organization_id'), 'subscriptions', ['organization_id'], unique=False)
    op.create_table('cms_entries',
    sa.Column('kind', sa.String(length=8), nullable=False),
    sa.Column('locale', sa.String(length=2), nullable=False),
    sa.Column('slug', sa.String(length=120), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('summary', sa.String(length=400), nullable=True),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('category', sa.String(length=60), nullable=True),
    sa.Column('tags', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('status', sa.String(length=10), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('author_user_id', sa.Uuid(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['author_user_id'], ['users.id'], name=op.f('fk_cms_entries_author_user_id_users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_cms_entries')),
    sa.UniqueConstraint('kind', 'locale', 'slug', name='uq_cms_entries_kind_locale_slug')
    )
    op.create_index('ix_cms_entries_public', 'cms_entries', ['kind', 'locale', 'status', 'published_at'], unique=False)
    op.create_table('developer_access_requests',
    sa.Column('reference', sa.String(length=24), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('organization_id', sa.Uuid(), nullable=True),
    sa.Column('environment', sa.String(length=10), nullable=False),
    sa.Column('company_name', sa.String(length=120), nullable=False),
    sa.Column('country', sa.String(length=80), nullable=True),
    sa.Column('use_case', sa.Text(), nullable=False),
    sa.Column('expected_volume', sa.String(length=40), nullable=True),
    sa.Column('status', sa.String(length=10), nullable=False),
    sa.Column('decision_note', sa.String(length=500), nullable=True),
    sa.Column('decided_by_user_id', sa.Uuid(), nullable=True),
    sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['decided_by_user_id'], ['users.id'], name=op.f('fk_developer_access_requests_decided_by_user_id_users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_developer_access_requests_organization_id_organizations'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_developer_access_requests_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_developer_access_requests')),
    sa.UniqueConstraint('reference', name=op.f('uq_developer_access_requests_reference'))
    )
    op.create_index(op.f('ix_developer_access_requests_user_id'), 'developer_access_requests', ['user_id'], unique=False)
    op.create_table('invoices',
    sa.Column('number', sa.String(length=24), nullable=True),
    sa.Column('organization_id', sa.Uuid(), nullable=False),
    sa.Column('subscription_id', sa.Uuid(), nullable=False),
    sa.Column('period_start', sa.Date(), nullable=False),
    sa.Column('period_end', sa.Date(), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('status', sa.String(length=10), nullable=False),
    sa.Column('lines', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('subtotal', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('tax_rate', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.Column('tax_amount', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('total', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('issued_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('due_at', sa.Date(), nullable=True),
    sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('voided_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_invoices_organization_id_organizations'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], name=op.f('fk_invoices_subscription_id_subscriptions'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_invoices')),
    sa.UniqueConstraint('number', name=op.f('uq_invoices_number'))
    )
    op.create_index(op.f('ix_invoices_organization_id'), 'invoices', ['organization_id'], unique=False)
    op.create_table('public_requests',
    sa.Column('reference', sa.String(length=24), nullable=False),
    sa.Column('kind', sa.String(length=10), nullable=False),
    sa.Column('request_type', sa.String(length=30), nullable=False),
    sa.Column('team', sa.String(length=12), nullable=False),
    sa.Column('locale', sa.String(length=2), nullable=False),
    sa.Column('status', sa.String(length=12), nullable=False),
    sa.Column('country', sa.String(length=80), nullable=True),
    sa.Column('sector', sa.String(length=60), nullable=True),
    sa.Column('volume', sa.String(length=40), nullable=True),
    sa.Column('services', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('payload', sa.Text(), nullable=False),
    sa.Column('email_hash', sa.String(length=64), nullable=False),
    sa.Column('ip_hash', sa.String(length=64), nullable=True),
    sa.Column('consent_privacy', sa.Boolean(), nullable=False),
    sa.Column('consent_marketing', sa.Boolean(), nullable=False),
    sa.Column('consent_version', sa.String(length=20), nullable=True),
    sa.Column('assigned_to_user_id', sa.Uuid(), nullable=True),
    sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['assigned_to_user_id'], ['users.id'], name=op.f('fk_public_requests_assigned_to_user_id_users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_public_requests')),
    sa.UniqueConstraint('reference', name=op.f('uq_public_requests_reference'))
    )
    op.create_index(op.f('ix_public_requests_email_hash'), 'public_requests', ['email_hash'], unique=False)
    op.create_index('ix_public_requests_status_created', 'public_requests', ['status', 'created_at'], unique=False)
    op.create_table('user_mfa',
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('secret', sa.Text(), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.Column('recovery_codes', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('enrolled_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_used_step', sa.Integer(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_user_mfa_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user_mfa')),
    sa.UniqueConstraint('user_id', name=op.f('uq_user_mfa_user_id'))
    )
    op.create_table('credit_notes',
    sa.Column('number', sa.String(length=24), nullable=False),
    sa.Column('invoice_id', sa.Uuid(), nullable=False),
    sa.Column('organization_id', sa.Uuid(), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('amount', sa.Numeric(precision=14, scale=2), nullable=False),
    sa.Column('reason', sa.String(length=300), nullable=False),
    sa.Column('issued_by_user_id', sa.Uuid(), nullable=True),
    sa.Column('issued_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], name=op.f('fk_credit_notes_invoice_id_invoices'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['issued_by_user_id'], ['users.id'], name=op.f('fk_credit_notes_issued_by_user_id_users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_credit_notes_organization_id_organizations'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_credit_notes')),
    sa.UniqueConstraint('number', name=op.f('uq_credit_notes_number'))
    )
    op.create_index(op.f('ix_credit_notes_invoice_id'), 'credit_notes', ['invoice_id'], unique=False)
    op.create_table('public_request_events',
    sa.Column('request_id', sa.Uuid(), nullable=False),
    sa.Column('seq', sa.Integer(), nullable=False),
    sa.Column('event_type', sa.String(length=30), nullable=False),
    sa.Column('from_status', sa.String(length=12), nullable=True),
    sa.Column('to_status', sa.String(length=12), nullable=True),
    sa.Column('actor_user_id', sa.Uuid(), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['request_id'], ['public_requests.id'], name=op.f('fk_public_request_events_request_id_public_requests'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_public_request_events'))
    )
    op.create_index(op.f('ix_public_request_events_request_id'), 'public_request_events', ['request_id'], unique=False)
    op.add_column('api_keys', sa.Column('environment', sa.String(length=10), nullable=False, server_default='production'))
    op.add_column('kyc_cases', sa.Column('is_sandbox', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('organizations', sa.Column('production_enabled', sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column('users', sa.Column('token_version', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'token_version')
    op.drop_column('organizations', 'production_enabled')
    op.drop_column('kyc_cases', 'is_sandbox')
    op.drop_column('api_keys', 'environment')
    op.drop_index(op.f('ix_public_request_events_request_id'), table_name='public_request_events')
    op.drop_table('public_request_events')
    op.drop_index(op.f('ix_credit_notes_invoice_id'), table_name='credit_notes')
    op.drop_table('credit_notes')
    op.drop_table('user_mfa')
    op.drop_index('ix_public_requests_status_created', table_name='public_requests')
    op.drop_index(op.f('ix_public_requests_email_hash'), table_name='public_requests')
    op.drop_table('public_requests')
    op.drop_index(op.f('ix_invoices_organization_id'), table_name='invoices')
    op.drop_table('invoices')
    op.drop_index(op.f('ix_developer_access_requests_user_id'), table_name='developer_access_requests')
    op.drop_table('developer_access_requests')
    op.drop_index('ix_cms_entries_public', table_name='cms_entries')
    op.drop_table('cms_entries')
    op.drop_index(op.f('ix_subscriptions_organization_id'), table_name='subscriptions')
    op.drop_table('subscriptions')
    op.drop_index('ix_email_outbox_due', table_name='email_outbox')
    op.drop_table('email_outbox')
    op.drop_table('document_counters')
    op.drop_table('billing_plans')
