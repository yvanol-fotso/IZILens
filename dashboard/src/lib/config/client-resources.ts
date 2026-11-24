import { Briefcase, Activity, Bell, LifeBuoy, Receipt, CreditCard, Gauge, Webhook, Terminal, Fingerprint } from '@lucide/svelte';
import type { ResourceDef } from './resources';

const SERVICES = ['kyc', 'kyb', 'biometrics', 'monitoring'];
const STATUS = ['pending', 'processing', 'approved', 'rejected', 'manual_review', 'failed', 'expired'];

/**
 * Ressources de l'espace client (/app/[resource]). Les clients n'ont PAS de rôle administrateur :
 * ils soumettent, consultent, paient et repartent. Toute décision de revue est prise par le personnel Kafintech.
 */
export const CLIENT_RESOURCES: ResourceDef[] = [
	{
		key: 'kyb', scope: 'client', endpoint: '/kyb/cases', read: 'kyb:read', icon: Briefcase, exportable: true,
		cols: [{ key: 'legal_name', link: true }, { key: 'country' }, { key: 'registration_number', type: 'mono' }, { key: 'reference', type: 'mono' }, { key: 'status', type: 'status' }, { key: 'created_at', type: 'datetime' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'status', type: 'select', options: STATUS }, { key: 'created', type: 'range' }],
		create: { permission: 'kyb:create', fields: [
			{ name: 'legal_name', type: 'text', required: true }, { name: 'country', type: 'text', required: true, hint: 'ISO 3166-1 alpha-2' },
			{ name: 'registration_number', type: 'text', required: true }, { name: 'legal_form', type: 'text' }, { name: 'reference', type: 'text', hint: 'Votre référence interne' },
			{ name: 'documents', type: 'repeater', fields: [{ name: 'document_type', type: 'select', options: ['registration_certificate', 'articles_of_association', 'ownership_structure', 'proof_of_address', 'other'], required: true }, { name: 'file', type: 'file', accept: 'application/pdf,image/*', required: true }] },
			{ name: 'directors', type: 'repeater', fields: [{ name: 'full_name', type: 'text', required: true }, { name: 'role', type: 'text', required: true }, { name: 'nationality', type: 'text' }, { name: 'birth_date', type: 'date' }] },
			{ name: 'ubos', type: 'repeater', fields: [{ name: 'full_name', type: 'text', required: true }, { name: 'ownership_percent', type: 'number', min: 0, max: 100, required: true }, { name: 'nationality', type: 'text' }, { name: 'birth_date', type: 'date' }] }
		] },
		actions: [{ id: 'provide_info', method: 'POST', path: '/kyb/cases/{id}/info', permission: 'kyb:create', fields: [{ name: 'message', type: 'textarea', required: true }, { name: 'file', type: 'file', accept: 'application/pdf,image/*' }], when: { key: 'status', in: ['manual_review', 'pending'] } }],
		detail: {
			sections: [{ key: 'company', fields: [{ key: 'legal_name' }, { key: 'country' }, { key: 'registration_number', type: 'mono' }, { key: 'legal_form' }, { key: 'reference', type: 'mono' }, { key: 'status', type: 'status' }, { key: 'created_at', type: 'datetime' }] }],
			related: [
				{ key: 'directors', path: '/kyb/cases/{id}/directors', cols: [{ key: 'full_name' }, { key: 'role', type: 'badge' }, { key: 'nationality' }, { key: 'status', type: 'status' }] },
				{ key: 'ubos', path: '/kyb/cases/{id}/ubos', cols: [{ key: 'full_name' }, { key: 'ownership_percent', type: 'percent' }, { key: 'nationality' }] },
				{ key: 'documents', path: '/kyb/cases/{id}/documents', cols: [{ key: 'document_type', type: 'badge' }, { key: 'file_name' }, { key: 'created_at', type: 'datetime' }] },
				{ key: 'events', path: '/kyb/cases/{id}/events', cols: [{ key: 'created_at', type: 'datetime' }, { key: 'event', type: 'mono' }, { key: 'detail' }] }
			]
		}
	},
	{
		key: 'monitoring', scope: 'client', endpoint: '/monitoring/requests', read: 'monitoring:read', icon: Activity, exportable: true,
		cols: [{ key: 'reference', type: 'mono', link: true }, { key: 'service', type: 'badge' }, { key: 'status', type: 'status' }, { key: 'blocked', type: 'bool' }, { key: 'created_at', type: 'datetime' }, { key: 'updated_at', type: 'datetime' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'status', type: 'select', options: ['pending', 'processing', 'approved', 'rejected', 'manual_review'] }, { key: 'service', type: 'select', options: SERVICES }, { key: 'pending_only', type: 'select', options: ['true'] }],
		detail: { sections: [{ key: 'request', fields: [{ key: 'reference', type: 'mono' }, { key: 'service', type: 'badge' }, { key: 'status', type: 'status' }, { key: 'blocked', type: 'bool' }, { key: 'created_at', type: 'datetime' }, { key: 'updated_at', type: 'datetime' }] }], related: [{ key: 'events', path: '/monitoring/requests/{id}/events', cols: [{ key: 'created_at', type: 'datetime' }, { key: 'event', type: 'mono' }, { key: 'detail' }] }, { key: 'actions', path: '/monitoring/requests/{id}/actions', cols: [{ key: 'created_at', type: 'datetime' }, { key: 'action', type: 'mono' }, { key: 'actor' }] }] }
	},
	{
		key: 'alerts', scope: 'client', endpoint: '/monitoring/alerts', read: 'monitoring:read', icon: Bell, detail: false,
		cols: [{ key: 'created_at', type: 'datetime' }, { key: 'level', type: 'risk' }, { key: 'category', type: 'badge' }, { key: 'title' }, { key: 'reference', type: 'mono' }, { key: 'read', type: 'bool' }],
		filters: [{ key: 'read', type: 'select', options: ['false', 'true'] }],
		actions: [{ id: 'mark_read', method: 'POST', path: '/monitoring/alerts/{id}/read', permission: 'monitoring:read', when: { key: 'read', in: ['false'] } }]
	},
	{
		key: 'biometrics', scope: 'client', endpoint: '/biometrics/sessions', read: 'biometrics:use', icon: Fingerprint, exportable: true, detail: false,
		cols: [{ key: 'id', type: 'mono' }, { key: 'case_reference', type: 'mono' }, { key: 'created_at', type: 'datetime' }, { key: 'liveness_result', type: 'badge' }, { key: 'match_result', type: 'badge' }, { key: 'final_result', type: 'status' }, { key: 'failure_reason' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'final_result', type: 'select', options: ['passed', 'failed', 'review', 'expired'] }, { key: 'created', type: 'range' }]
	},
	{
		key: 'support', scope: 'client', endpoint: '/support/tickets', read: 'support:use', icon: LifeBuoy,
		cols: [{ key: 'reference', type: 'mono', link: true }, { key: 'subject' }, { key: 'category', type: 'badge' }, { key: 'priority', type: 'risk' }, { key: 'status', type: 'status' }, { key: 'updated_at', type: 'datetime' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'status', type: 'select', options: ['open', 'in_progress', 'waiting_for_customer', 'resolved', 'closed'] }],
		create: { permission: 'support:use', fields: [{ name: 'subject', type: 'text', required: true }, { name: 'category', type: 'select', options: ['incident', 'integration', 'billing', 'verification', 'other'], required: true }, { name: 'priority', type: 'select', options: ['low', 'medium', 'high'], required: true }, { name: 'message', type: 'textarea', required: true }, { name: 'attachment', type: 'file' }] },
		actions: [
			{ id: 'reply', method: 'POST', path: '/support/tickets/{id}/messages', permission: 'support:use', tone: 'brand', fields: [{ name: 'message', type: 'textarea', required: true }, { name: 'attachment', type: 'file' }], when: { key: 'status', in: ['open', 'in_progress', 'waiting_for_customer'] } },
			{ id: 'close', method: 'POST', path: '/support/tickets/{id}/close', permission: 'support:use', when: { key: 'status', in: ['open', 'in_progress', 'waiting_for_customer', 'resolved'] } }
		],
		detail: { sections: [{ key: 'ticket', fields: [{ key: 'reference', type: 'mono' }, { key: 'subject' }, { key: 'category', type: 'badge' }, { key: 'priority', type: 'risk' }, { key: 'status', type: 'status' }, { key: 'created_at', type: 'datetime' }] }], related: [{ key: 'messages', path: '/support/tickets/{id}/messages', cols: [{ key: 'created_at', type: 'datetime' }, { key: 'author' }, { key: 'message' }] }] }
	},
	{
		key: 'invoices', scope: 'client', endpoint: '/billing/invoices', read: 'billing:read', icon: Receipt, exportable: true,
		cols: [{ key: 'number', type: 'mono', link: true }, { key: 'period' }, { key: 'total', type: 'money', currencyKey: 'currency' }, { key: 'status', type: 'status' }, { key: 'issued_at', type: 'date' }, { key: 'due_at', type: 'date' }, { key: 'pdf_url', type: 'file' }],
		filters: [{ key: 'status', type: 'select', options: ['pending', 'paid', 'due', 'overdue'] }, { key: 'period', type: 'search' }],
		detail: {
			sections: [{ key: 'invoice', fields: [{ key: 'number', type: 'mono' }, { key: 'period' }, { key: 'currency' }, { key: 'subscription_amount', type: 'money' }, { key: 'consumption_amount', type: 'money' }, { key: 'options_amount', type: 'money' }, { key: 'integration_fee', type: 'money' }, { key: 'discount', type: 'money' }, { key: 'minimum_applied', type: 'bool' }, { key: 'total', type: 'money' }, { key: 'status', type: 'status' }, { key: 'issued_at', type: 'date' }, { key: 'due_at', type: 'date' }] }],
			related: [{ key: 'lines', path: '/billing/invoices/{id}/lines', cols: [{ key: 'service', type: 'badge' }, { key: 'description' }, { key: 'quantity', type: 'number' }, { key: 'unit_price', type: 'money', currencyKey: 'currency' }, { key: 'amount', type: 'money', currencyKey: 'currency' }] }]
		}
	},
	{
		key: 'payments', scope: 'client', endpoint: '/billing/payments', read: 'billing:read', icon: CreditCard, exportable: true, detail: false,
		cols: [{ key: 'created_at', type: 'datetime' }, { key: 'invoice_number', type: 'mono' }, { key: 'amount', type: 'money', currencyKey: 'currency' }, { key: 'method', type: 'badge' }, { key: 'status', type: 'status' }, { key: 'reference', type: 'mono' }]
	},
	{
		key: 'usage', scope: 'client', endpoint: '/billing/usage', read: 'billing:read', icon: Gauge, exportable: true, detail: false,
		cols: [{ key: 'created_at', type: 'datetime' }, { key: 'service', type: 'badge' }, { key: 'transaction_id', type: 'mono' }, { key: 'status', type: 'status' }, { key: 'quantity', type: 'number' }, { key: 'unit_price', type: 'money', currencyKey: 'currency' }, { key: 'amount', type: 'money', currencyKey: 'currency' }, { key: 'environment', type: 'badge' }],
		filters: [{ key: 'service', type: 'select', options: SERVICES }, { key: 'environment', type: 'select', options: ['production', 'sandbox'] }, { key: 'created', type: 'range' }]
	},
	{
		key: 'webhooks', scope: 'client', endpoint: '/developers/webhooks', read: 'developers:manage', icon: Webhook,
		cols: [{ key: 'url', type: 'mono', link: true }, { key: 'events', type: 'list' }, { key: 'environment', type: 'badge' }, { key: 'status', type: 'status' }, { key: 'last_delivery_status', type: 'badge' }],
		create: { permission: 'developers:manage', fields: [{ name: 'url', type: 'url', required: true }, { name: 'environment', type: 'select', options: ['sandbox', 'production'], required: true }, { name: 'events', type: 'multiselect', required: true, options: ['verification.created', 'verification.started', 'document.submitted', 'verification.completed', 'result.available', 'verification.needs_review'] }] },
		edit: true,
		actions: [
			{ id: 'rotate_secret', method: 'POST', path: '/developers/webhooks/{id}/rotate-secret', permission: 'developers:manage', reason: false },
			{ id: 'test', method: 'POST', path: '/developers/webhooks/{id}/test', permission: 'developers:manage' },
			{ id: 'disable', method: 'POST', path: '/developers/webhooks/{id}/disable', permission: 'developers:manage', tone: 'danger', when: { key: 'status', in: ['active', 'failing'] } },
			{ id: 'enable', method: 'POST', path: '/developers/webhooks/{id}/enable', permission: 'developers:manage', tone: 'brand', when: { key: 'status', in: ['disabled'] } }
		],
		detail: { sections: [{ key: 'webhook', fields: [{ key: 'url', type: 'mono' }, { key: 'events', type: 'list' }, { key: 'environment', type: 'badge' }, { key: 'status', type: 'status' }, { key: 'created_at', type: 'datetime' }] }], related: [{ key: 'deliveries', path: '/developers/webhooks/{id}/deliveries', cols: [{ key: 'created_at', type: 'datetime' }, { key: 'event', type: 'mono' }, { key: 'status_code', type: 'number' }, { key: 'attempts', type: 'number' }, { key: 'status', type: 'status' }] }] }
	},
	{
		key: 'api-logs', scope: 'client', endpoint: '/developers/logs', read: 'developers:manage', icon: Terminal, exportable: true, detail: false,
		cols: [{ key: 'created_at', type: 'datetime' }, { key: 'key_prefix', type: 'mono' }, { key: 'method', type: 'badge' }, { key: 'path', type: 'mono' }, { key: 'status_code', type: 'number' }, { key: 'latency_ms', type: 'number' }, { key: 'environment', type: 'badge' }],
		filters: [{ key: 'search', type: 'search' }, { key: 'environment', type: 'select', options: ['production', 'sandbox'] }, { key: 'errors_only', type: 'select', options: ['true'] }, { key: 'created', type: 'range' }]
	}
];

export const clientResource = (key: string) => CLIENT_RESOURCES.find((r) => r.key === key);
