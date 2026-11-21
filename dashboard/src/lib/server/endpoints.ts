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
	audit: '/audit-logs',
	health: '/health'
} as const;
