import type { Field } from './resources';
import type { Permission } from './permissions';

/** Pages de configuration (GET → valeurs, PUT → enregistrement versionné + audit). Source du contrat backend. */
export interface ConfigPage { key: string; endpoint: string; read: Permission; write: Permission; critical: boolean; sections: { key: string; fields: Field[] }[] }

const CURRENCIES = ['CAD', 'USD', 'EUR', 'XOF', 'XAF', 'GBP'];

export const CONFIG_PAGES: Record<string, ConfigPage> = {
	platform: {
		key: 'platform', endpoint: '/admin/platform/settings', read: 'adm:platform', write: 'adm:platform', critical: true,
		sections: [
			{ key: 'modules', fields: ['kyc', 'kyb', 'biometrics', 'monitoring', 'aml', 'fraud'].map((m) => ({ name: `module_${m}`, type: 'switch' as const })) },
			{ key: 'environments', fields: [{ name: 'sandbox_enabled', type: 'switch' }, { name: 'production_enabled', type: 'switch' }, { name: 'maintenance_mode', type: 'switch', hint: 'Bloque les nouvelles vérifications clients' }] },
			{ key: 'localization', fields: [{ name: 'languages', type: 'multiselect', options: ['fr', 'en'], required: true }, { name: 'default_language', type: 'select', options: ['fr', 'en'], required: true }, { name: 'currencies', type: 'multiselect', options: CURRENCIES, required: true }, { name: 'default_currency', type: 'select', options: CURRENCIES, required: true }] },
			{ key: 'operations', fields: [{ name: 'max_upload_mb', type: 'number', min: 1, max: 100 }, { name: 'case_expiry_days', type: 'number', min: 1 }, { name: 'ocr_review_threshold', type: 'number', min: 0, max: 1, hint: 'Seuil de confiance OCR sous lequel un dossier passe en revue manuelle (0 à 1)' }] }
		]
	},
	settings: {
		key: 'settings', endpoint: '/admin/settings', read: 'adm:settings', write: 'adm:settings', critical: true,
		sections: [
			{ key: 'sessions', fields: [{ name: 'session_timeout_minutes', type: 'number', min: 5, max: 480 }, { name: 'mfa_methods', type: 'multiselect', options: ['totp', 'passkey'], required: true }, { name: 'password_min_length', type: 'number', min: 12, max: 128 }] },
			{ key: 'network', fields: [{ name: 'ip_policy', type: 'select', options: ['off', 'audit', 'enforce'] }, { name: 'ip_allowlist', type: 'textarea', hint: 'Une adresse ou plage CIDR par ligne' }] },
			{ key: 'retention', fields: [{ name: 'document_retention_days', type: 'number', min: 1 }, { name: 'audit_retention_days', type: 'number', min: 365 }] },
			{ key: 'alerts', fields: [{ name: 'email_alerts', type: 'switch' }, { name: 'alert_recipients', type: 'textarea', hint: 'Une adresse e-mail par ligne' }, { name: 'sensitive_change_alerts', type: 'switch' }] },
			{ key: 'breakglass', fields: [{ name: 'breakglass_enabled', type: 'switch', hint: 'Compte de secours : accès exceptionnel, audit obligatoire' }, { name: 'breakglass_notify', type: 'textarea', hint: 'E-mails notifiés à chaque utilisation' }] }
		]
	},
	providers: {
		key: 'providers', endpoint: '/admin/providers', read: 'adm:providers', write: 'adm:providers', critical: true,
		sections: [
			{ key: 'ocr', fields: [{ name: 'ocr_enabled', type: 'switch' }, { name: 'ocr_provider', type: 'text' }, { name: 'ocr_api_url', type: 'url' }, { name: 'ocr_api_key', type: 'password', secret: true }, { name: 'ocr_cost_per_unit', type: 'number', min: 0 }, { name: 'ocr_cost_currency', type: 'select', options: CURRENCIES }] },
			{ key: 'bio', fields: [{ name: 'bio_mode', type: 'select', options: ['internal', 'hybrid', 'external'], required: true }, { name: 'bio_enabled', type: 'switch' }, { name: 'bio_provider', type: 'text' }, { name: 'bio_api_url', type: 'url' }, { name: 'bio_api_key', type: 'password', secret: true }, { name: 'bio_cost_per_session', type: 'number', min: 0 }, { name: 'bio_cost_currency', type: 'select', options: CURRENCIES }] },
			{ key: 'aml', fields: [{ name: 'aml_enabled', type: 'switch' }, { name: 'aml_provider', type: 'text' }, { name: 'aml_api_key', type: 'password', secret: true }, { name: 'aml_lists', type: 'multiselect', options: ['sanctions', 'pep', 'adverse_media'] }] },
			{ key: 'cloud', fields: [{ name: 'cloud_provider', type: 'text' }, { name: 'cloud_region', type: 'text' }, { name: 'storage_bucket', type: 'text' }, { name: 'cloud_credentials', type: 'password', secret: true }] },
			{ key: 'messaging', fields: [{ name: 'email_provider', type: 'text' }, { name: 'email_api_key', type: 'password', secret: true }, { name: 'webhook_signing_secret', type: 'password', secret: true }] }
		]
	}
};

export const REPORTS = ['activity', 'financial', 'per_client', 'per_country', 'kyc_kyb', 'biometrics', 'incidents', 'provider_costs', 'technical', 'security'];
export const PRICING_CURRENCIES = CURRENCIES;
