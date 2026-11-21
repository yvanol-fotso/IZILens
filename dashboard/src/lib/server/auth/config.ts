import { dev } from '$app/environment';
import { env } from '$env/dynamic/private';

/** Point unique de configuration de l'authentification (variables d'environnement + constantes). */
export const authConfig = {
	cookies: { access: 'izi_at', refresh: 'izi_rt', oauth: 'izi_oauth' },
	paths: {
		login: '/login',
		afterLogin: '/app',
		afterLoginAdmin: '/app/admin',
		oauth: '/api/auth/oauth'
	},
	get loginFormat(): 'json' | 'form' {
		return env.BACKEND_LOGIN_FORMAT === 'form' ? 'form' : 'json';
	},
	get secureCookies(): boolean {
		return env.AUTH_COOKIE_SECURE ? env.AUTH_COOKIE_SECURE === 'true' : !dev;
	},
	get google() {
		return {
			clientId: env.GOOGLE_CLIENT_ID ?? '',
			clientSecret: env.GOOGLE_CLIENT_SECRET ?? '',
			redirectUri: env.GOOGLE_REDIRECT_URI ?? ''
		};
	},
	get googleConfigured(): boolean {
		return !!(env.GOOGLE_CLIENT_ID && env.GOOGLE_CLIENT_SECRET);
	}
};
