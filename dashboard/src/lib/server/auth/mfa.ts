import type { Cookies } from '@sveltejs/kit';
import { authConfig } from './config';

export const MFA_COOKIE = 'izi_mfa';
const opts = () => ({ path: '/login', httpOnly: true, sameSite: 'lax' as const, secure: authConfig.secureCookies, maxAge: 300 });

/** Défi MFA en attente (jeton court émis par le backend après un mot de passe / SSO valide). */
export const setMfaChallenge = (cookies: Cookies, token: string, next: string) => cookies.set(MFA_COOKIE, JSON.stringify({ token, next }), opts());
export function getMfaChallenge(cookies: Cookies): { token: string; next: string } | null {
	try { const v = JSON.parse(cookies.get(MFA_COOKIE) ?? 'null'); return v?.token ? v : null; } catch { return null; }
}
export const clearMfaChallenge = (cookies: Cookies) => cookies.delete(MFA_COOKIE, { path: '/login' });
