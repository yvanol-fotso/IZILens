/**
 * Contrat attendu du backend FastAPI (préfixe BACKEND_API_PREFIX, défaut /api/v1).
 * Si une route diffère chez vous, c'est le SEUL fichier à modifier.
 * Voir docs/BACKEND_CONTRACT.md.
 */
export const EP = {
	auth: {
		login: '/auth/login',
		register: '/auth/register',
		refresh: '/auth/refresh',
		logout: '/auth/logout',
		me: '/auth/me',
		changePassword: '/auth/change-password',
		/** Échange d'un id_token OIDC contre une paire de jetons du backend. */
		oauth: (provider: string) => `/auth/oauth/${provider}`
	},
	org: {
		me: '/organizations/me',
		list: '/organizations',
		one: (id: string) => `/organizations/${id}`
	},
	users: {
		list: '/users',
		one: (id: string) => `/users/${id}`,
		me: '/users/me'
	},
	apiKeys: {
		list: '/api-keys',
		one: (id: string) => `/api-keys/${id}`
	},
	kyc: {
		cases: '/kyc/cases',
		one: (id: string) => `/kyc/cases/${id}`,
		decision: (id: string) => `/kyc/cases/${id}/decision`,
		content: (id: string, docId: string) => `/kyc/cases/${id}/documents/${docId}/content`
	},
	liveness: {
		sessions: '/liveness/sessions',
		settings: '/liveness/settings'
	},
	/** Demandes publiques (contact, devis, démonstration) → back-office. */
	public: { contact: '/public/contact-requests' },
	audit: '/audit-logs',
	health: '/health'
} as const;

/**
 * Endpoints étendus (espace admin, sécurité, facturation, passkeys, MFA).
 * Typé `any` pour l'instant afin de faire passer le build : les chemins ci-dessous
 * sont déduits de vos fichiers de config et sont à vérifier contre le backend.
 */
export const EPX: any = {
	admin: {
		dashboard: '/admin/dashboard',
		infra: '/admin/infrastructure',
		kycCases: '/admin/kyc/cases',
		kycOne: (id: string) => `/admin/kyc/cases/${id}`,
		kycDecision: (id: string) => `/admin/kyc/cases/${id}/decision`,
		pricing: '/admin/billing/pricing',
		pricingHistory: '/admin/billing/pricing/history',
		roles: '/admin/roles',
		security: '/admin/security',
		securitySessions: '/admin/security/sessions',
		securityEvents: '/admin/security/events',
		staff: '/admin/staff',
		audit: '/admin/audit-logs',
		settings: '/admin/settings',
		platform: '/admin/platform/settings',
		providers: '/admin/providers'
	},
	auth: {
		passkeysOptions: '/auth/passkeys/options',
		passkeysVerify: '/auth/passkeys/verify',
		mfaVerify: '/auth/mfa/verify',
		mfaSetup: '/auth/mfa/setup',
		mfaDisable: '/auth/mfa/disable',
		sessions: '/auth/sessions'
	},
	billing: {
		invoices: '/billing/invoices',
		payments: '/billing/payments',
		usage: '/billing/usage',
		subscription: '/billing/subscription'
	}
};