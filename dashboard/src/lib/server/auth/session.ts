import type { Cookies } from '@sveltejs/kit';
import type { TokenPair } from '$lib/types/auth';
import { authConfig } from './config';

export const ACCESS_COOKIE = authConfig.cookies.access;
export const REFRESH_COOKIE = authConfig.cookies.refresh;
export const OAUTH_COOKIE = authConfig.cookies.oauth;
export { safeNext } from './policy';

export function decodeJwt<T = Record<string, any>>(token: string): T | null {
	try {
		const part = token.split('.')[1];
		return JSON.parse(Buffer.from(part.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf8')) as T;
	} catch {
		return null;
	}
}

/** true si le jeton est expiré (ou expire dans `skew` secondes). Un jeton opaque n'expire jamais ici. */
export function isExpired(token: string, skew = 15): boolean {
	const exp = decodeJwt(token)?.exp;
	return typeof exp === 'number' ? exp * 1000 - skew * 1000 < Date.now() : false;
}

const base = () => ({ path: '/', httpOnly: true, sameSite: 'lax' as const, secure: authConfig.secureCookies });

function ttl(token: string, fallback: number): number {
	const exp = decodeJwt(token)?.exp;
	return typeof exp === 'number' ? Math.max(60, Math.floor(exp - Date.now() / 1000)) : fallback;
}

export function setSession(cookies: Cookies, tokens: TokenPair) {
	cookies.set(ACCESS_COOKIE, tokens.access_token, { ...base(), maxAge: ttl(tokens.access_token, tokens.expires_in ?? 3600) });
	if (tokens.refresh_token) {
		cookies.set(REFRESH_COOKIE, tokens.refresh_token, { ...base(), maxAge: ttl(tokens.refresh_token, 60 * 60 * 24 * 30) });
	}
}

export function clearSession(cookies: Cookies) {
	cookies.delete(ACCESS_COOKIE, { path: '/' });
	cookies.delete(REFRESH_COOKIE, { path: '/' });
}

export const oauthCookieOptions = () => ({ ...base(), path: authConfig.paths.oauth, maxAge: 600 });
