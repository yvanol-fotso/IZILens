import { Building2, FileCheck2, Briefcase, Fingerprint, Activity, Scale, ListChecks, ShieldAlert, ShieldQuestion, Receipt, CreditCard, FileMinus2, Repeat, Gauge, Coins, KeyRound, ScrollText, Terminal, UserCog, Bell, Inbox, LifeBuoy, Newspaper, BookOpen, CircleHelp, Lightbulb, Download, Webhook, UsersRound, MonitorSmartphone, TriangleAlert, FileClock, UserRoundCheck } from '@lucide/svelte';
import type { Action, Field, ResourceDef } from './resources';

const STATUS_CASE = ['pending', 'processing', 'approved', 'rejected', 'manual_review', 'failed', 'expired'];
const COUNTRIES_HINT = 'ISO 3166-1 alpha-2';
const SERVICES = ['kyc', 'kyb', 'biometrics', 'monitoring'];
const CURRENCIES = ['CAD', 'USD', 'EUR', 'XOF', 'XAF', 'GBP'];
const PLANS = ['starter', 'business', 'enterprise'];
const DEPARTMENTS = ['sales', 'partnerships', 'integration', 'institutional', 'other'];
const REQ_STATUS = ['new', 'assigned', 'in_progress', 'waiting_for_customer', 'resolved', 'closed'];
const sector = ['banks', 'fintech', 'micro', 'insurance', 'telecom', 'ecommerce', 'platforms', 'other'];
const reason: Pick<Action, 'reason'> = { reason: true };

const reviewFields: Field[] = [{ name: 'evidence', type: 'textarea', hint: 'Éléments justificatifs de la décision' }];

export const ADMIN_RESOURCES: ResourceDef[] = [
	// ── Clients & entreprises ───────────────────────────────────────────────
	{
		key: 'clients', scope: 'admin', endpoint: '/admin/clients', read: 'adm:clients', icon: Building2, exportable: true,
		cols: [{ key: 'name', link: true }, { key: 'country' }, { key: 'sector', type: 'badge' }, { key: 'plan', type: 'badge' }, { key: 'services', type: 'list' }, { key: 'verification_count', type: 'number' }, { key: 'status', type: 'status' }, { key: 'created_at', type: 'date' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'status', type: 'select', options: ['active', 'suspended', 'pending_validation'] }, { key: 'plan', type: 'select', options: PLANS }, { key: 'country', type: 'search' }],
		create: { permission: 'adm:clients:write', fields: [
			{ name: 'name', type: 'text', required: true }, { name: 'country', type: 'text', required: true, hint: COUNTRIES_HINT }, { name: 'sector', type: 'select', options: sector },
			{ name: 'representative_name', type: 'text', required: true }, { name: 'email', type: 'email', required: true }, { name: 'phone', type: 'text' },
			{ name: 'plan', type: 'select', options: PLANS, required: true }, { name: 'currency', type: 'select', options: CURRENCIES, required: true }, { name: 'services', type: 'multiselect', options: SERVICES }
		] },
		edit: true,
		actions: [
			{ id: 'suspend', method: 'POST', path: '/admin/clients/{id}/suspend', permission: 'adm:clients:write', tone: 'danger', ...reason, critical: true, when: { key: 'status', in: ['active'] } },
			{ id: 'activate', method: 'POST', path: '/admin/clients/{id}/activate', permission: 'adm:clients:write', tone: 'brand', ...reason, when: { key: 'status', in: ['suspended', 'pending_validation'] } },
			{ id: 'verify_documents', method: 'POST', path: '/admin/clients/{id}/verify-documents', permission: 'adm:clients:write', fields: [{ name: 'result', type: 'select', options: ['approved', 'rejected', 'more_info'], required: true }], reason: true },
			{ id: 'change_plan', method: 'POST', path: '/admin/clients/{id}/plan', permission: 'adm:billing:write', fields: [{ name: 'plan', type: 'select', options: PLANS, required: true }, { name: 'effective_from', type: 'date' }], reason: true },
			{ id: 'add_note', method: 'POST', path: '/admin/clients/{id}/notes', permission: 'adm:clients:write', fields: [{ name: 'note', type: 'textarea', required: true }] }
		],
		detail: {
			sections: [
				{ key: 'identity', fields: [{ key: 'id', type: 'mono' }, { key: 'name' }, { key: 'country' }, { key: 'sector', type: 'badge' }, { key: 'created_at', type: 'datetime' }, { key: 'status', type: 'status' }] },
				{ key: 'contact', fields: [{ key: 'representative_name' }, { key: 'email' }, { key: 'phone' }] },
				{ key: 'commercial', fields: [{ key: 'plan', type: 'badge' }, { key: 'currency' }, { key: 'services', type: 'list' }, { key: 'verification_count', type: 'number' }, { key: 'production_enabled', type: 'bool' }] }
			],
			related: [
				{ key: 'consumption', path: '/admin/clients/{id}/consumption', cols: [{ key: 'service', type: 'badge' }, { key: 'period' }, { key: 'quantity', type: 'number' }, { key: 'amount', type: 'money', currencyKey: 'currency' }] },
				{ key: 'invoices', path: '/admin/clients/{id}/invoices', cols: [{ key: 'number', type: 'mono' }, { key: 'period' }, { key: 'total', type: 'money', currencyKey: 'currency' }, { key: 'status', type: 'status' }] },
				{ key: 'users', path: '/admin/clients/{id}/users', cols: [{ key: 'full_name' }, { key: 'email' }, { key: 'role', type: 'badge' }, { key: 'last_login_at', type: 'datetime' }] },
				{ key: 'notes', path: '/admin/clients/{id}/notes', cols: [{ key: 'created_at', type: 'datetime' }, { key: 'author' }, { key: 'note' }] },
				{ key: 'activity', path: '/admin/clients/{id}/activity', cols: [{ key: 'created_at', type: 'datetime' }, { key: 'action', type: 'mono' }, { key: 'actor' }] }
			]
		}
	},
	// ── KYC (revue sur page dédiée) ──────────────────────────────────────────
	{
		key: 'kyc', scope: 'admin', endpoint: '/admin/kyc/cases', read: 'adm:kyc', icon: FileCheck2, exportable: true, detailHref: '/admin/kyc/{id}',
		cols: [{ key: 'reference', type: 'mono', link: true }, { key: 'client_name' }, { key: 'country' }, { key: 'document_type', type: 'badge' }, { key: 'ocr_confidence', type: 'percent' }, { key: 'document_result', type: 'badge' }, { key: 'biometric_result', type: 'badge' }, { key: 'risk_score', type: 'number' }, { key: 'status', type: 'status' }, { key: 'created_at', type: 'datetime' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'status', type: 'select', options: STATUS_CASE }, { key: 'country', type: 'search' }, { key: 'client_id', type: 'search' }, { key: 'created', type: 'range' }]
	},
	// ── KYB ─────────────────────────────────────────────────────────────────
	{
		key: 'kyb', scope: 'admin', endpoint: '/admin/kyb/cases', read: 'adm:kyb', icon: Briefcase, exportable: true,
		cols: [{ key: 'legal_name', link: true }, { key: 'country' }, { key: 'registration_number', type: 'mono' }, { key: 'client_name' }, { key: 'status', type: 'status' }, { key: 'created_at', type: 'datetime' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'status', type: 'select', options: STATUS_CASE }, { key: 'country', type: 'search' }, { key: 'created', type: 'range' }],
		actions: [
			{ id: 'approve', method: 'POST', path: '/admin/kyb/cases/{id}/decision', permission: 'adm:kyb:review', tone: 'brand', fields: [{ name: 'decision', type: 'select', options: ['approved'], required: true }, ...reviewFields], reason: true, when: { key: 'status', in: ['manual_review', 'pending', 'processing'] } },
			{ id: 'reject', method: 'POST', path: '/admin/kyb/cases/{id}/decision', permission: 'adm:kyb:review', tone: 'danger', fields: [{ name: 'decision', type: 'select', options: ['rejected'], required: true }, ...reviewFields], reason: true, when: { key: 'status', in: ['manual_review', 'pending', 'processing'] } },
			{ id: 'request_info', method: 'POST', path: '/admin/kyb/cases/{id}/request-info', permission: 'adm:kyb:review', fields: [{ name: 'message', type: 'textarea', required: true }] }
		],
		detail: {
			sections: [
				{ key: 'company', fields: [{ key: 'legal_name' }, { key: 'country' }, { key: 'registration_number', type: 'mono' }, { key: 'legal_form' }, { key: 'client_name' }, { key: 'status', type: 'status' }, { key: 'created_at', type: 'datetime' }] },
				{ key: 'decision', fields: [{ key: 'decided_by' }, { key: 'decided_at', type: 'datetime' }, { key: 'decision_reason' }] }
			],
			related: [
				{ key: 'directors', path: '/admin/kyb/cases/{id}/directors', cols: [{ key: 'full_name' }, { key: 'role', type: 'badge' }, { key: 'nationality' }, { key: 'status', type: 'status' }] },
				{ key: 'ubos', path: '/admin/kyb/cases/{id}/ubos', cols: [{ key: 'full_name' }, { key: 'ownership_percent', type: 'percent' }, { key: 'nationality' }, { key: 'relationship' }] },
				{ key: 'documents', path: '/admin/kyb/cases/{id}/documents', cols: [{ key: 'document_type', type: 'badge' }, { key: 'file_name' }, { key: 'result', type: 'badge' }, { key: 'created_at', type: 'datetime' }] },
				{ key: 'history', path: '/admin/kyb/cases/{id}/history', cols: [{ key: 'created_at', type: 'datetime' }, { key: 'actor' }, { key: 'action', type: 'mono' }, { key: 'reason' }] }
			]
		}
	},
	// ── Biométrie ───────────────────────────────────────────────────────────
	{
		key: 'biometrics', scope: 'admin', endpoint: '/admin/biometrics/sessions', read: 'adm:biometrics', icon: Fingerprint, exportable: true,
		cols: [{ key: 'id', type: 'mono', link: true }, { key: 'client_name' }, { key: 'created_at', type: 'datetime' }, { key: 'liveness_result', type: 'badge' }, { key: 'match_result', type: 'badge' }, { key: 'final_result', type: 'status' }, { key: 'failure_reason' }, { key: 'engine', type: 'badge' }, { key: 'provider' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'final_result', type: 'select', options: ['passed', 'failed', 'review', 'expired'] }, { key: 'engine', type: 'select', options: ['internal', 'external'] }, { key: 'created', type: 'range' }],
		detail: { sections: [{ key: 'session', fields: [{ key: 'id', type: 'mono' }, { key: 'client_name' }, { key: 'created_at', type: 'datetime' }, { key: 'liveness_result', type: 'badge' }, { key: 'match_score', type: 'percent' }, { key: 'match_result', type: 'badge' }, { key: 'final_result', type: 'status' }, { key: 'failure_reason' }, { key: 'engine', type: 'badge' }, { key: 'provider' }] }] }
	},
	// ── Monitoring ──────────────────────────────────────────────────────────
	{
		key: 'monitoring', scope: 'admin', endpoint: '/admin/monitoring/requests', read: 'adm:monitoring', icon: Activity, exportable: true,
		cols: [{ key: 'reference', type: 'mono', link: true }, { key: 'client_name' }, { key: 'service', type: 'badge' }, { key: 'status', type: 'status' }, { key: 'blocked', type: 'bool' }, { key: 'age_minutes', type: 'number' }, { key: 'updated_at', type: 'datetime' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'status', type: 'select', options: STATUS_CASE }, { key: 'service', type: 'select', options: SERVICES }, { key: 'blocked', type: 'select', options: ['true', 'false'] }],
		actions: [
			{ id: 'relaunch', method: 'POST', path: '/admin/monitoring/requests/{id}/relaunch', permission: 'adm:kyc:review', ...reason, when: { key: 'blocked', in: ['true'] } },
			{ id: 'note', method: 'POST', path: '/admin/monitoring/requests/{id}/interventions', permission: 'adm:kyc:review', fields: [{ name: 'note', type: 'textarea', required: true }] }
		],
		detail: { sections: [{ key: 'request', fields: [{ key: 'reference', type: 'mono' }, { key: 'client_name' }, { key: 'service', type: 'badge' }, { key: 'status', type: 'status' }, { key: 'blocked', type: 'bool' }, { key: 'age_minutes', type: 'number' }] }], related: [{ key: 'events', path: '/admin/monitoring/requests/{id}/events', cols: [{ key: 'created_at', type: 'datetime' }, { key: 'event', type: 'mono' }, { key: 'detail' }] }, { key: 'interventions', path: '/admin/monitoring/requests/{id}/interventions', cols: [{ key: 'created_at', type: 'datetime' }, { key: 'author' }, { key: 'note' }] }] }
	},
	// ── Risque ──────────────────────────────────────────────────────────────
	{
		key: 'risk', scope: 'admin', endpoint: '/admin/risk/cases', read: 'adm:risk', icon: Scale, exportable: true,
		cols: [{ key: 'reference', type: 'mono', link: true }, { key: 'client_name' }, { key: 'service', type: 'badge' }, { key: 'risk_level', type: 'risk' }, { key: 'score', type: 'number' }, { key: 'rule_version', type: 'mono' }, { key: 'status', type: 'status' }, { key: 'created_at', type: 'datetime' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'risk_level', type: 'select', options: ['low', 'medium', 'high'] }, { key: 'status', type: 'select', options: ['open', 'in_review', 'decided'] }],
		actions: [{ id: 'decide', method: 'POST', path: '/admin/risk/cases/{id}/decision', permission: 'adm:risk:write', fields: [{ name: 'decision', type: 'select', options: ['accept', 'reject', 'escalate'], required: true }], reason: true, when: { key: 'status', in: ['open', 'in_review'] } }],
		detail: { sections: [{ key: 'case', fields: [{ key: 'reference', type: 'mono' }, { key: 'client_name' }, { key: 'risk_level', type: 'risk' }, { key: 'score', type: 'number' }, { key: 'rule_version', type: 'mono' }, { key: 'status', type: 'status' }] }], related: [{ key: 'signals', path: '/admin/risk/cases/{id}/signals', cols: [{ key: 'rule' }, { key: 'weight', type: 'number' }, { key: 'detail' }] }, { key: 'history', path: '/admin/risk/cases/{id}/history', cols: [{ key: 'created_at', type: 'datetime' }, { key: 'actor' }, { key: 'decision', type: 'badge' }, { key: 'reason' }] }] }
	},
	{
		key: 'risk-rules', scope: 'admin', endpoint: '/admin/risk/rules', read: 'adm:risk', icon: ListChecks,
		cols: [{ key: 'name', link: true }, { key: 'service', type: 'badge' }, { key: 'weight', type: 'number' }, { key: 'version', type: 'mono' }, { key: 'enabled', type: 'bool' }, { key: 'updated_at', type: 'datetime' }],
		filters: [{ key: 'service', type: 'select', options: SERVICES }],
		create: { permission: 'adm:risk:write', fields: [{ name: 'name', type: 'text', required: true }, { name: 'service', type: 'select', options: SERVICES, required: true }, { name: 'condition', type: 'textarea', required: true, hint: 'Expression de la règle (JSON)' }, { name: 'weight', type: 'number', min: 0, max: 100, required: true }, { name: 'enabled', type: 'switch' }] },
		edit: true,
		actions: [{ id: 'publish', method: 'POST', path: '/admin/risk/rules/{id}/publish', permission: 'adm:risk:write', tone: 'brand', ...reason }],
		detail: { sections: [{ key: 'rule', fields: [{ key: 'name' }, { key: 'service', type: 'badge' }, { key: 'condition', type: 'mono' }, { key: 'weight', type: 'number' }, { key: 'version', type: 'mono' }, { key: 'enabled', type: 'bool' }] }], related: [{ key: 'versions', path: '/admin/risk/rules/{id}/versions', cols: [{ key: 'version', type: 'mono' }, { key: 'created_at', type: 'datetime' }, { key: 'author' }, { key: 'reason' }] }] }
	},
	// ── AML ─────────────────────────────────────────────────────────────────
	{
		key: 'aml', scope: 'admin', endpoint: '/admin/aml/alerts', read: 'adm:aml', icon: ShieldAlert, exportable: true,
		cols: [{ key: 'case_reference', type: 'mono', link: true }, { key: 'client_name' }, { key: 'subject_name' }, { key: 'list_type', type: 'badge' }, { key: 'match_score', type: 'percent' }, { key: 'status', type: 'status' }, { key: 'created_at', type: 'datetime' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'list_type', type: 'select', options: ['sanctions', 'pep'] }, { key: 'status', type: 'select', options: ['open', 'in_review', 'confirmed', 'dismissed', 'escalated'] }],
		actions: [
			{ id: 'confirm', method: 'POST', path: '/admin/aml/alerts/{id}/decision', permission: 'adm:aml:review', tone: 'danger', fields: [{ name: 'decision', type: 'select', options: ['confirmed'], required: true }], reason: true, critical: true, when: { key: 'status', in: ['open', 'in_review'] } },
			{ id: 'dismiss', method: 'POST', path: '/admin/aml/alerts/{id}/decision', permission: 'adm:aml:review', fields: [{ name: 'decision', type: 'select', options: ['dismissed'], required: true }], reason: true, when: { key: 'status', in: ['open', 'in_review'] } },
			{ id: 'escalate', method: 'POST', path: '/admin/aml/alerts/{id}/decision', permission: 'adm:aml:review', fields: [{ name: 'decision', type: 'select', options: ['escalated'], required: true }], reason: true, when: { key: 'status', in: ['open', 'in_review'] } }
		],
		detail: { sections: [{ key: 'alert', fields: [{ key: 'case_reference', type: 'mono' }, { key: 'subject_name' }, { key: 'list_type', type: 'badge' }, { key: 'matched_entry' }, { key: 'match_score', type: 'percent' }, { key: 'status', type: 'status' }] }], related: [{ key: 'history', path: '/admin/aml/alerts/{id}/history', cols: [{ key: 'created_at', type: 'datetime' }, { key: 'actor' }, { key: 'decision', type: 'badge' }, { key: 'reason' }] }] }
	},
	{
		key: 'fraud', scope: 'admin', endpoint: '/admin/fraud/signals', read: 'adm:fraud', icon: ShieldQuestion, exportable: true,
		cols: [{ key: 'signal_type', type: 'badge' }, { key: 'client_name' }, { key: 'subject_ref', type: 'mono', link: true }, { key: 'severity', type: 'risk' }, { key: 'status', type: 'status' }, { key: 'created_at', type: 'datetime' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'signal_type', type: 'select', options: ['suspicious_document', 'inconsistency', 'repeated_attempts', 'biometric_anomaly', 'technical'] }, { key: 'severity', type: 'select', options: ['low', 'medium', 'high'] }, { key: 'status', type: 'select', options: ['open', 'reviewed', 'dismissed'] }],
		actions: [{ id: 'review', method: 'POST', path: '/admin/fraud/signals/{id}/review', permission: 'adm:kyc:review', fields: [{ name: 'decision', type: 'select', options: ['reviewed', 'dismissed'], required: true }], reason: true, when: { key: 'status', in: ['open'] } }],
		detail: { sections: [{ key: 'signal', fields: [{ key: 'signal_type', type: 'badge' }, { key: 'client_name' }, { key: 'subject_ref', type: 'mono' }, { key: 'severity', type: 'risk' }, { key: 'status', type: 'status' }, { key: 'detail' }] }] }
	},
	// ── Facturation ─────────────────────────────────────────────────────────
	{
		key: 'invoices', scope: 'admin', endpoint: '/admin/billing/invoices', read: 'adm:billing', icon: Receipt, exportable: true,
		cols: [{ key: 'number', type: 'mono', link: true }, { key: 'client_name' }, { key: 'period' }, { key: 'subtotal', type: 'money', currencyKey: 'currency' }, { key: 'minimum_applied', type: 'bool' }, { key: 'total', type: 'money', currencyKey: 'currency' }, { key: 'status', type: 'status' }, { key: 'due_at', type: 'date' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'status', type: 'select', options: ['draft', 'pending', 'paid', 'due', 'overdue', 'void'] }, { key: 'currency', type: 'select', options: CURRENCIES }, { key: 'period', type: 'search' }],
		actions: [
			{ id: 'mark_paid', method: 'POST', path: '/admin/billing/invoices/{id}/payments', permission: 'adm:billing:write', tone: 'brand', fields: [{ name: 'reference', type: 'text', required: true }, { name: 'amount', type: 'number' }], when: { key: 'status', in: ['pending', 'due', 'overdue'] } },
			{ id: 'send_reminder', method: 'POST', path: '/admin/billing/invoices/{id}/remind', permission: 'adm:billing:write', when: { key: 'status', in: ['pending', 'due', 'overdue'] } },
			{ id: 'credit_note', method: 'POST', path: '/admin/billing/invoices/{id}/credit-notes', permission: 'adm:billing:write', tone: 'danger', fields: [{ name: 'amount', type: 'number', required: true, min: 0 }], reason: true, critical: true },
			{ id: 'void', method: 'POST', path: '/admin/billing/invoices/{id}/void', permission: 'adm:billing:write', tone: 'danger', reason: true, critical: true, when: { key: 'status', in: ['draft', 'pending'] } }
		],
		detail: {
			sections: [{ key: 'invoice', fields: [{ key: 'number', type: 'mono' }, { key: 'client_name' }, { key: 'period' }, { key: 'currency' }, { key: 'subscription_amount', type: 'money' }, { key: 'consumption_amount', type: 'money' }, { key: 'options_amount', type: 'money' }, { key: 'integration_fee', type: 'money' }, { key: 'discount', type: 'money' }, { key: 'subtotal', type: 'money' }, { key: 'minimum_applied', type: 'bool' }, { key: 'total', type: 'money' }, { key: 'status', type: 'status' }, { key: 'issued_at', type: 'date' }, { key: 'due_at', type: 'date' }, { key: 'pricing_version', type: 'mono' }] }],
			related: [
				{ key: 'lines', path: '/admin/billing/invoices/{id}/lines', cols: [{ key: 'service', type: 'badge' }, { key: 'description' }, { key: 'quantity', type: 'number' }, { key: 'unit_price', type: 'money', currencyKey: 'currency' }, { key: 'amount', type: 'money', currencyKey: 'currency' }] },
				{ key: 'payments', path: '/admin/billing/invoices/{id}/payments', cols: [{ key: 'created_at', type: 'datetime' }, { key: 'reference', type: 'mono' }, { key: 'amount', type: 'money', currencyKey: 'currency' }, { key: 'method', type: 'badge' }] },
				{ key: 'credit_notes', path: '/admin/billing/invoices/{id}/credit-notes', cols: [{ key: 'number', type: 'mono' }, { key: 'created_at', type: 'datetime' }, { key: 'amount', type: 'money', currencyKey: 'currency' }, { key: 'reason' }] }
			]
		}
	},
	{
		key: 'payments', scope: 'admin', endpoint: '/admin/billing/payments', read: 'adm:billing', icon: CreditCard, exportable: true, detail: false,
		cols: [{ key: 'created_at', type: 'datetime' }, { key: 'client_name' }, { key: 'invoice_number', type: 'mono' }, { key: 'amount', type: 'money', currencyKey: 'currency' }, { key: 'method', type: 'badge' }, { key: 'status', type: 'status' }, { key: 'reference', type: 'mono' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'status', type: 'select', options: ['succeeded', 'failed', 'pending', 'refunded'] }, { key: 'currency', type: 'select', options: CURRENCIES }]
	},
	{
		key: 'credit-notes', scope: 'admin', endpoint: '/admin/billing/credit-notes', read: 'adm:billing', icon: FileMinus2, exportable: true, detail: false,
		cols: [{ key: 'number', type: 'mono' }, { key: 'created_at', type: 'datetime' }, { key: 'client_name' }, { key: 'invoice_number', type: 'mono' }, { key: 'amount', type: 'money', currencyKey: 'currency' }, { key: 'reason' }, { key: 'issued_by' }],
		filters: [{ key: 'search', type: 'search' }]
	},
	{
		key: 'subscriptions', scope: 'admin', endpoint: '/admin/billing/subscriptions', read: 'adm:billing', icon: Repeat, exportable: true,
		cols: [{ key: 'client_name', link: true }, { key: 'plan', type: 'badge' }, { key: 'billing_cycle', type: 'badge' }, { key: 'amount', type: 'money', currencyKey: 'currency' }, { key: 'monitoring_option', type: 'bool' }, { key: 'status', type: 'status' }, { key: 'renews_at', type: 'date' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'plan', type: 'select', options: PLANS }, { key: 'status', type: 'select', options: ['active', 'suspended', 'cancelled'] }],
		actions: [
			{ id: 'change_cycle', method: 'POST', path: '/admin/billing/subscriptions/{id}/cycle', permission: 'adm:billing:write', fields: [{ name: 'billing_cycle', type: 'select', options: ['monthly', 'annual'], required: true }], reason: true },
			{ id: 'toggle_service', method: 'POST', path: '/admin/billing/subscriptions/{id}/services', permission: 'adm:billing:write', fields: [{ name: 'service', type: 'select', options: SERVICES, required: true }, { name: 'billing_enabled', type: 'switch' }], reason: true },
			{ id: 'set_limits', method: 'PUT', path: '/admin/billing/subscriptions/{id}/limits', permission: 'adm:billing:write', fields: [{ name: 'kyc_monthly_limit', type: 'number', min: 0 }, { name: 'kyb_monthly_limit', type: 'number', min: 0 }, { name: 'biometrics_monthly_limit', type: 'number', min: 0 }], reason: true },
			{ id: 'custom_pricing', method: 'PUT', path: '/admin/billing/subscriptions/{id}/custom-pricing', permission: 'adm:pricing:write', fields: [{ name: 'discount_percent', type: 'number', min: 0, max: 100 }, { name: 'kyc_unit_price', type: 'number', min: 0 }, { name: 'kyb_unit_price', type: 'number', min: 0 }, { name: 'biometrics_unit_price', type: 'number', min: 0 }, { name: 'enterprise_minimum', type: 'number', min: 0 }, { name: 'integration_fee_enabled', type: 'switch' }], reason: true, critical: true }
		],
		detail: { sections: [{ key: 'subscription', fields: [{ key: 'client_name' }, { key: 'plan', type: 'badge' }, { key: 'billing_cycle', type: 'badge' }, { key: 'currency' }, { key: 'amount', type: 'money' }, { key: 'monitoring_option', type: 'bool' }, { key: 'status', type: 'status' }, { key: 'renews_at', type: 'date' }, { key: 'custom_pricing', type: 'bool' }] }], related: [{ key: 'limits', path: '/admin/billing/subscriptions/{id}/limits', cols: [{ key: 'service', type: 'badge' }, { key: 'monthly_limit', type: 'number' }, { key: 'used', type: 'number' }, { key: 'billing_enabled', type: 'bool' }] }] }
	},
	{
		key: 'usage', scope: 'admin', endpoint: '/admin/billing/usage-records', read: 'adm:billing', icon: Gauge, exportable: true, detail: false,
		cols: [{ key: 'created_at', type: 'datetime' }, { key: 'client_name' }, { key: 'transaction_id', type: 'mono' }, { key: 'service', type: 'badge' }, { key: 'status', type: 'status' }, { key: 'quantity', type: 'number' }, { key: 'unit_price', type: 'money', currencyKey: 'currency' }, { key: 'amount', type: 'money', currencyKey: 'currency' }, { key: 'environment', type: 'badge' }, { key: 'billable', type: 'bool' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'service', type: 'select', options: SERVICES }, { key: 'environment', type: 'select', options: ['production', 'sandbox'] }, { key: 'billable', type: 'select', options: ['true', 'false'] }, { key: 'created', type: 'range' }]
	},
	{
		key: 'provider-costs', scope: 'admin', endpoint: '/admin/billing/provider-costs', read: 'adm:billing', icon: Coins, exportable: true, detail: false,
		cols: [{ key: 'provider', type: 'badge' }, { key: 'service', type: 'badge' }, { key: 'period' }, { key: 'units', type: 'number' }, { key: 'unit_cost', type: 'money', currencyKey: 'currency' }, { key: 'cost', type: 'money', currencyKey: 'currency' }],
		filters: [{ key: 'provider', type: 'search' }, { key: 'period', type: 'search' }]
	},
	// ── API & développeurs ──────────────────────────────────────────────────
	{
		key: 'access-requests', scope: 'admin', endpoint: '/admin/developers/access-requests', read: 'adm:api', icon: UserRoundCheck, exportable: true,
		cols: [{ key: 'organization_name', link: true }, { key: 'contact_email' }, { key: 'services', type: 'list' }, { key: 'status', type: 'status' }, { key: 'created_at', type: 'datetime' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'status', type: 'select', options: ['pending', 'approved', 'rejected'] }],
		actions: [
			{ id: 'approve', method: 'POST', path: '/admin/developers/access-requests/{id}/approve', permission: 'adm:api:write', tone: 'brand', fields: [{ name: 'services', type: 'multiselect', options: SERVICES, required: true }, { name: 'production', type: 'switch' }], reason: true, critical: true, when: { key: 'status', in: ['pending'] } },
			{ id: 'reject', method: 'POST', path: '/admin/developers/access-requests/{id}/reject', permission: 'adm:api:write', tone: 'danger', reason: true, when: { key: 'status', in: ['pending'] } }
		],
		detail: { sections: [{ key: 'request', fields: [{ key: 'organization_name' }, { key: 'contact_email' }, { key: 'project' }, { key: 'services', type: 'list' }, { key: 'intended_use' }, { key: 'technical_info' }, { key: 'status', type: 'status' }, { key: 'created_at', type: 'datetime' }, { key: 'decided_by' }, { key: 'decision_reason' }] }] }
	},
	{
		key: 'developer-accounts', scope: 'admin', endpoint: '/admin/developers/accounts', read: 'adm:api', icon: UsersRound, detail: false,
		cols: [{ key: 'full_name' }, { key: 'email' }, { key: 'organization_name' }, { key: 'sandbox_access', type: 'bool' }, { key: 'production_access', type: 'bool' }, { key: 'created_at', type: 'date' }],
		filters: [{ key: 'search', type: 'search' }]
	},
	{
		key: 'api-keys', scope: 'admin', endpoint: '/admin/developers/keys', read: 'adm:api', icon: KeyRound, exportable: true,
		cols: [{ key: 'prefix', type: 'mono', link: true }, { key: 'client_name' }, { key: 'environment', type: 'badge' }, { key: 'status', type: 'status' }, { key: 'last_used_at', type: 'datetime' }, { key: 'created_at', type: 'date' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'environment', type: 'select', options: ['production', 'sandbox'] }, { key: 'status', type: 'select', options: ['active', 'revoked', 'expired'] }],
		actions: [{ id: 'revoke', method: 'POST', path: '/admin/developers/keys/{id}/revoke', permission: 'adm:api:write', tone: 'danger', reason: true, critical: true, when: { key: 'status', in: ['active'] } }],
		detail: { sections: [{ key: 'key', fields: [{ key: 'prefix', type: 'mono' }, { key: 'client_name' }, { key: 'environment', type: 'badge' }, { key: 'status', type: 'status' }, { key: 'last_used_at', type: 'datetime' }, { key: 'created_at', type: 'datetime' }, { key: 'revoked_at', type: 'datetime' }] }] }
	},
	{
		key: 'api-logs', scope: 'admin', endpoint: '/admin/developers/logs', read: 'adm:api', icon: Terminal, exportable: true, detail: false,
		cols: [{ key: 'created_at', type: 'datetime' }, { key: 'client_name' }, { key: 'key_prefix', type: 'mono' }, { key: 'method', type: 'badge' }, { key: 'path', type: 'mono' }, { key: 'status_code', type: 'number' }, { key: 'latency_ms', type: 'number' }, { key: 'environment', type: 'badge' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'environment', type: 'select', options: ['production', 'sandbox'] }, { key: 'errors_only', type: 'select', options: ['true'] }, { key: 'created', type: 'range' }]
	},
	{
		key: 'webhooks', scope: 'admin', endpoint: '/admin/developers/webhooks', read: 'adm:api', icon: Webhook, detail: false,
		cols: [{ key: 'client_name' }, { key: 'url', type: 'mono' }, { key: 'events', type: 'list' }, { key: 'environment', type: 'badge' }, { key: 'status', type: 'status' }, { key: 'last_delivery_status', type: 'badge' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'status', type: 'select', options: ['active', 'disabled', 'failing'] }],
		actions: [{ id: 'disable', method: 'POST', path: '/admin/developers/webhooks/{id}/disable', permission: 'adm:api:write', tone: 'danger', reason: true, when: { key: 'status', in: ['active', 'failing'] } }]
	},
	// ── Personnel & sécurité ────────────────────────────────────────────────
	{
		key: 'staff', scope: 'admin', endpoint: '/admin/staff', read: 'adm:staff', icon: UserCog, exportable: true,
		cols: [{ key: 'full_name', link: true }, { key: 'email' }, { key: 'role', type: 'badge' }, { key: 'status', type: 'status' }, { key: 'mfa_enabled', type: 'bool' }, { key: 'last_login_at', type: 'datetime' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'role', type: 'select', options: ['super_admin', 'platform_admin', 'compliance_officer', 'kyc_analyst', 'risk_officer', 'finance_manager', 'support_agent', 'tech_admin', 'read_only'] }, { key: 'status', type: 'select', options: ['active', 'inactive'] }],
		create: { permission: 'adm:staff', fields: [{ name: 'full_name', type: 'text', required: true }, { name: 'email', type: 'email', required: true }, { name: 'role', type: 'select', required: true, options: ['platform_admin', 'compliance_officer', 'kyc_analyst', 'risk_officer', 'finance_manager', 'support_agent', 'tech_admin', 'read_only'] }] },
		edit: true,
		actions: [
			{ id: 'change_role', method: 'POST', path: '/admin/staff/{id}/role', permission: 'adm:roles', fields: [{ name: 'role', type: 'select', required: true, options: ['super_admin', 'platform_admin', 'compliance_officer', 'kyc_analyst', 'risk_officer', 'finance_manager', 'support_agent', 'tech_admin', 'read_only'] }], reason: true, critical: true },
			{ id: 'deactivate', method: 'POST', path: '/admin/staff/{id}/deactivate', permission: 'adm:staff', tone: 'danger', reason: true, critical: true, when: { key: 'status', in: ['active'] } },
			{ id: 'activate', method: 'POST', path: '/admin/staff/{id}/activate', permission: 'adm:staff', tone: 'brand', reason: true, when: { key: 'status', in: ['inactive'] } },
			{ id: 'reset_mfa', method: 'POST', path: '/admin/staff/{id}/reset-mfa', permission: 'adm:staff', reason: true, critical: true },
			{ id: 'revoke_sessions', method: 'POST', path: '/admin/staff/{id}/revoke-sessions', permission: 'adm:security:write', reason: true }
		],
		detail: { sections: [{ key: 'staff', fields: [{ key: 'full_name' }, { key: 'email' }, { key: 'role', type: 'badge' }, { key: 'status', type: 'status' }, { key: 'mfa_enabled', type: 'bool' }, { key: 'last_login_at', type: 'datetime' }, { key: 'created_at', type: 'datetime' }] }], related: [{ key: 'logins', path: '/admin/staff/{id}/logins', cols: [{ key: 'created_at', type: 'datetime' }, { key: 'ip_address', type: 'mono' }, { key: 'device' }, { key: 'result', type: 'badge' }] }, { key: 'actions', path: '/admin/staff/{id}/audit', cols: [{ key: 'created_at', type: 'datetime' }, { key: 'action', type: 'mono' }, { key: 'resource_type' }, { key: 'result', type: 'badge' }] }] }
	},
	{
		key: 'sessions', scope: 'admin', endpoint: '/admin/security/sessions', read: 'adm:security', icon: MonitorSmartphone, detail: false,
		cols: [{ key: 'user_name' }, { key: 'role', type: 'badge' }, { key: 'ip_address', type: 'mono' }, { key: 'device' }, { key: 'started_at', type: 'datetime' }, { key: 'last_seen_at', type: 'datetime' }],
		filters: [{ key: 'search', type: 'search' }],
		actions: [{ id: 'revoke', method: 'POST', path: '/admin/security/sessions/{id}/revoke', permission: 'adm:security:write', tone: 'danger', reason: true }]
	},
	{
		key: 'security-events', scope: 'admin', endpoint: '/admin/security/events', read: 'adm:security', icon: TriangleAlert, exportable: true, detail: false,
		cols: [{ key: 'created_at', type: 'datetime' }, { key: 'event_type', type: 'badge' }, { key: 'user_name' }, { key: 'ip_address', type: 'mono' }, { key: 'severity', type: 'risk' }, { key: 'detail' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'event_type', type: 'select', options: ['suspicious_login', 'failed_login', 'permission_change', 'sensitive_access', 'admin_activity', 'incident'] }, { key: 'severity', type: 'select', options: ['low', 'medium', 'high'] }, { key: 'created', type: 'range' }]
	},
	{
		key: 'audit', scope: 'admin', endpoint: '/admin/audit-logs', read: 'adm:audit', icon: ScrollText, exportable: true,
		cols: [{ key: 'created_at', type: 'datetime' }, { key: 'actor', link: true }, { key: 'action', type: 'mono' }, { key: 'resource_type' }, { key: 'resource_id', type: 'mono' }, { key: 'result', type: 'badge' }, { key: 'ip_address', type: 'mono' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'result', type: 'select', options: ['success', 'failure', 'denied'] }, { key: 'resource_type', type: 'search' }, { key: 'created', type: 'range' }],
		detail: { sections: [{ key: 'event', fields: [{ key: 'id', type: 'mono' }, { key: 'created_at', type: 'datetime' }, { key: 'actor' }, { key: 'actor_type', type: 'badge' }, { key: 'action', type: 'mono' }, { key: 'resource_type' }, { key: 'resource_id', type: 'mono' }, { key: 'result', type: 'badge' }, { key: 'ip_address', type: 'mono' }, { key: 'request_id', type: 'mono' }, { key: 'details', type: 'mono' }] }] }
	},
	{
		key: 'notifications', scope: 'admin', endpoint: '/admin/notifications', read: 'adm:notifications', icon: Bell, detail: false,
		cols: [{ key: 'created_at', type: 'datetime' }, { key: 'level', type: 'risk' }, { key: 'category', type: 'badge' }, { key: 'title' }, { key: 'read', type: 'bool' }],
		filters: [{ key: 'category', type: 'select', options: ['new_verification', 'pending_case', 'review_needed', 'technical_failure', 'api_incident', 'risk_alert', 'unpaid_invoice', 'payment_issue', 'provider_down'] }, { key: 'read', type: 'select', options: ['false', 'true'] }],
		actions: [{ id: 'mark_read', method: 'POST', path: '/admin/notifications/{id}/read', permission: 'adm:notifications', when: { key: 'read', in: ['false'] } }]
	},
	// ── Demandes & support ──────────────────────────────────────────────────
	{
		key: 'requests', scope: 'admin', endpoint: '/admin/requests', read: 'adm:requests', icon: Inbox, exportable: true,
		cols: [{ key: 'reference', type: 'mono', link: true }, { key: 'request_type', type: 'badge' }, { key: 'full_name' }, { key: 'company' }, { key: 'country' }, { key: 'department', type: 'badge' }, { key: 'status', type: 'status' }, { key: 'assignee_name' }, { key: 'created_at', type: 'datetime' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'status', type: 'select', options: REQ_STATUS }, { key: 'department', type: 'select', options: DEPARTMENTS }],
		actions: [
			{ id: 'assign', method: 'POST', path: '/admin/requests/{id}/assign', permission: 'adm:requests', fields: [{ name: 'department', type: 'select', options: DEPARTMENTS }, { name: 'assignee_id', type: 'staff' }] },
			{ id: 'set_status', method: 'POST', path: '/admin/requests/{id}/status', permission: 'adm:requests', fields: [{ name: 'status', type: 'select', options: REQ_STATUS, required: true }] },
			{ id: 'comment', method: 'POST', path: '/admin/requests/{id}/comments', permission: 'adm:requests', fields: [{ name: 'comment', type: 'textarea', required: true }] }
		],
		detail: { sections: [{ key: 'request', fields: [{ key: 'reference', type: 'mono' }, { key: 'request_type', type: 'badge' }, { key: 'status', type: 'status' }, { key: 'department', type: 'badge' }, { key: 'assignee_name' }, { key: 'created_at', type: 'datetime' }] }, { key: 'sender', fields: [{ key: 'full_name' }, { key: 'company' }, { key: 'email' }, { key: 'phone' }, { key: 'country' }, { key: 'role' }, { key: 'sector' }, { key: 'estimated_volume' }, { key: 'services', type: 'list' }] }, { key: 'content', fields: [{ key: 'subject' }, { key: 'message' }] }], related: [{ key: 'comments', path: '/admin/requests/{id}/comments', cols: [{ key: 'created_at', type: 'datetime' }, { key: 'author' }, { key: 'comment' }] }, { key: 'history', path: '/admin/requests/{id}/history', cols: [{ key: 'created_at', type: 'datetime' }, { key: 'actor' }, { key: 'action', type: 'mono' }] }] }
	},
	{
		key: 'support', scope: 'admin', endpoint: '/admin/support/tickets', read: 'adm:support', icon: LifeBuoy, exportable: true,
		cols: [{ key: 'reference', type: 'mono', link: true }, { key: 'client_name' }, { key: 'subject' }, { key: 'priority', type: 'risk' }, { key: 'status', type: 'status' }, { key: 'assignee_name' }, { key: 'updated_at', type: 'datetime' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'status', type: 'select', options: ['open', 'in_progress', 'waiting_for_customer', 'resolved', 'closed'] }, { key: 'priority', type: 'select', options: ['low', 'medium', 'high'] }],
		actions: [
			{ id: 'reply', method: 'POST', path: '/admin/support/tickets/{id}/messages', permission: 'adm:support', tone: 'brand', fields: [{ name: 'message', type: 'textarea', required: true }] },
			{ id: 'set_status', method: 'POST', path: '/admin/support/tickets/{id}/status', permission: 'adm:support', fields: [{ name: 'status', type: 'select', options: ['open', 'in_progress', 'waiting_for_customer', 'resolved', 'closed'], required: true }] },
			{ id: 'assign', method: 'POST', path: '/admin/support/tickets/{id}/assign', permission: 'adm:support', fields: [{ name: 'assignee_id', type: 'staff', required: true }] }
		],
		detail: { sections: [{ key: 'ticket', fields: [{ key: 'reference', type: 'mono' }, { key: 'client_name' }, { key: 'subject' }, { key: 'category', type: 'badge' }, { key: 'priority', type: 'risk' }, { key: 'status', type: 'status' }, { key: 'assignee_name' }, { key: 'created_at', type: 'datetime' }] }], related: [{ key: 'messages', path: '/admin/support/tickets/{id}/messages', cols: [{ key: 'created_at', type: 'datetime' }, { key: 'author' }, { key: 'message' }] }] }
	},
	// ── Contenu éditorial (page Ressources) ─────────────────────────────────
	{
		key: 'articles', scope: 'admin', endpoint: '/admin/content/articles', read: 'adm:content', icon: Newspaper,
		cols: [{ key: 'title_fr', link: true }, { key: 'category', type: 'badge' }, { key: 'author' }, { key: 'status', type: 'status' }, { key: 'publish_at', type: 'datetime' }, { key: 'views', type: 'number' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'status', type: 'select', options: ['draft', 'review', 'scheduled', 'published', 'archived'] }, { key: 'category', type: 'select', options: ['kyc', 'kyb', 'biometrics', 'aml', 'fraud', 'fintech', 'trust'] }],
		create: { permission: 'adm:content', fields: [{ name: 'title_fr', type: 'text', required: true }, { name: 'title_en', type: 'text', required: true }, { name: 'slug', type: 'text', required: true }, { name: 'category', type: 'select', options: ['kyc', 'kyb', 'biometrics', 'aml', 'fraud', 'fintech', 'trust'], required: true }, { name: 'author', type: 'text' }, { name: 'source_name', type: 'text', hint: 'Actualité externe : nom de la source' }, { name: 'source_url', type: 'url', hint: 'Lien vers l’original (obligatoire pour une actualité externe)' }, { name: 'summary_fr', type: 'textarea', required: true }, { name: 'summary_en', type: 'textarea', required: true }, { name: 'body_fr', type: 'textarea', required: true }, { name: 'body_en', type: 'textarea', required: true }, { name: 'cover', type: 'file', accept: 'image/*' }] },
		edit: true,
		actions: [
			{ id: 'publish', method: 'POST', path: '/admin/content/articles/{id}/publish', permission: 'adm:content', tone: 'brand', when: { key: 'status', in: ['draft', 'review', 'scheduled'] } },
			{ id: 'schedule', method: 'POST', path: '/admin/content/articles/{id}/schedule', permission: 'adm:content', fields: [{ name: 'publish_at', type: 'date', required: true }], when: { key: 'status', in: ['draft', 'review'] } },
			{ id: 'archive', method: 'POST', path: '/admin/content/articles/{id}/archive', permission: 'adm:content', tone: 'danger', when: { key: 'status', in: ['published'] } }
		],
		detail: { sections: [{ key: 'article', fields: [{ key: 'title_fr' }, { key: 'title_en' }, { key: 'slug', type: 'mono' }, { key: 'category', type: 'badge' }, { key: 'status', type: 'status' }, { key: 'publish_at', type: 'datetime' }, { key: 'source_url' }] }] }
	},
	{
		key: 'guides', scope: 'admin', endpoint: '/admin/content/guides', read: 'adm:content', icon: BookOpen,
		cols: [{ key: 'title_fr', link: true }, { key: 'access', type: 'badge' }, { key: 'status', type: 'status' }, { key: 'downloads', type: 'number' }, { key: 'updated_at', type: 'datetime' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'access', type: 'select', options: ['free', 'premium'] }, { key: 'status', type: 'select', options: ['draft', 'published', 'archived'] }],
		create: { permission: 'adm:content', fields: [{ name: 'title_fr', type: 'text', required: true }, { name: 'title_en', type: 'text', required: true }, { name: 'description_fr', type: 'textarea' }, { name: 'description_en', type: 'textarea' }, { name: 'access', type: 'select', options: ['free', 'premium'], required: true }, { name: 'file_fr', type: 'file', accept: 'application/pdf' }, { name: 'file_en', type: 'file', accept: 'application/pdf' }, { name: 'cover', type: 'file', accept: 'image/*' }] },
		edit: true,
		actions: [{ id: 'publish', method: 'POST', path: '/admin/content/guides/{id}/publish', permission: 'adm:content', tone: 'brand', when: { key: 'status', in: ['draft'] } }, { id: 'archive', method: 'POST', path: '/admin/content/guides/{id}/archive', permission: 'adm:content', tone: 'danger', when: { key: 'status', in: ['published'] } }],
		detail: { sections: [{ key: 'guide', fields: [{ key: 'title_fr' }, { key: 'title_en' }, { key: 'access', type: 'badge' }, { key: 'status', type: 'status' }, { key: 'downloads', type: 'number' }] }] }
	},
	{
		key: 'faq', scope: 'admin', endpoint: '/admin/content/faq', read: 'adm:content', icon: CircleHelp,
		cols: [{ key: 'question_fr', link: true }, { key: 'category', type: 'badge' }, { key: 'position', type: 'number' }, { key: 'status', type: 'status' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'category', type: 'select', options: ['general', 'kyc', 'kyb', 'biometrics', 'api', 'security', 'billing'] }],
		create: { permission: 'adm:content', fields: [{ name: 'category', type: 'select', options: ['general', 'kyc', 'kyb', 'biometrics', 'api', 'security', 'billing'], required: true }, { name: 'question_fr', type: 'text', required: true }, { name: 'question_en', type: 'text', required: true }, { name: 'answer_fr', type: 'textarea', required: true }, { name: 'answer_en', type: 'textarea', required: true }, { name: 'position', type: 'number', min: 0 }, { name: 'status', type: 'select', options: ['draft', 'published'] }] },
		edit: true,
		detail: { sections: [{ key: 'faq', fields: [{ key: 'category', type: 'badge' }, { key: 'question_fr' }, { key: 'question_en' }, { key: 'answer_fr' }, { key: 'answer_en' }, { key: 'status', type: 'status' }] }] }
	},
	{
		key: 'case-studies', scope: 'admin', endpoint: '/admin/content/case-studies', read: 'adm:content', icon: Lightbulb,
		cols: [{ key: 'title_fr', link: true }, { key: 'sector', type: 'badge' }, { key: 'illustrative', type: 'bool' }, { key: 'status', type: 'status' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'sector', type: 'select', options: sector }],
		create: { permission: 'adm:content', fields: [{ name: 'title_fr', type: 'text', required: true }, { name: 'title_en', type: 'text', required: true }, { name: 'sector', type: 'select', options: sector, required: true }, { name: 'context_fr', type: 'textarea' }, { name: 'context_en', type: 'textarea' }, { name: 'problem_fr', type: 'textarea' }, { name: 'problem_en', type: 'textarea' }, { name: 'solution_fr', type: 'textarea' }, { name: 'solution_en', type: 'textarea' }, { name: 'modules', type: 'multiselect', options: SERVICES }, { name: 'illustrative', type: 'switch', hint: 'Scénario illustratif (aucune référence client réelle sans preuve et autorisation)' }, { name: 'status', type: 'select', options: ['draft', 'published'] }] },
		edit: true,
		detail: { sections: [{ key: 'case', fields: [{ key: 'title_fr' }, { key: 'title_en' }, { key: 'sector', type: 'badge' }, { key: 'illustrative', type: 'bool' }, { key: 'status', type: 'status' }] }] }
	},
	{
		key: 'leads', scope: 'admin', endpoint: '/admin/content/download-leads', read: 'adm:content', icon: Download, exportable: true, detail: false,
		cols: [{ key: 'created_at', type: 'datetime' }, { key: 'full_name' }, { key: 'company' }, { key: 'email' }, { key: 'guide_title' }, { key: 'marketing_consent', type: 'bool' }],
		filters: [{ key: 'search', type: 'search' }]
	}
];

export const adminResource = (key: string) => ADMIN_RESOURCES.find((r) => r.key === key);
void FileClock;
