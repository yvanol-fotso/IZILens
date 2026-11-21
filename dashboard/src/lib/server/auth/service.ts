import type { Cookies } from '@sveltejs/kit';
import { BackendError, backendJson } from '../backend';
import { EP } from '../endpoints';
import { authConfig } from './config';
import { clearSession } from './session';
import type { Organization, SessionUser, TokenPair } from '$lib/types/auth';

export async function loginWithPassword(email: string, password: string): Promise<TokenPair> {
	if (authConfig.loginFormat === 'form') {
		return backendJson<TokenPair>(EP.auth.login, { method: 'POST', form: new URLSearchParams({ username: email, password }) });
	}
	return backendJson<TokenPair>(EP.auth.login, { method: 'POST', json: { email, password } });
}

export async function refreshTokens(refresh_token: string): Promise<TokenPair | null> {
	try {
		const tokens = await backendJson<TokenPair>(EP.auth.refresh, { method: 'POST', json: { refresh_token } });
		return { refresh_token, ...tokens };
	} catch {
		return null;
	}
}

export async function logoutEverywhere(cookies: Cookies, accessToken: string | null, refreshToken?: string) {
	if (accessToken) {
		try {
			await backendJson(EP.auth.logout, { method: 'POST', token: accessToken, json: refreshToken ? { refresh_token: refreshToken } : {} });
		} catch {
			/* meilleur effort : le backend n'a pas forcément de route logout */
		}
	}
	clearSession(cookies);
}

/** Accepte ["kyc"], {"kyc": true} ou null. */
export function normalizeModules(raw: unknown): string[] {
	if (Array.isArray(raw)) return raw.map(String);
	if (raw && typeof raw === 'object') return Object.entries(raw).filter(([, v]) => !!v).map(([k]) => k);
	return ['kyc', 'api'];
}

export function toOrganization(raw: any): Organization | null {
	if (!raw || typeof raw !== 'object' || !raw.id) return null;
	return {
		id: raw.id,
		name: raw.name ?? '—',
		slug: raw.slug ?? '',
		is_active: raw.is_active ?? true,
		enabled_modules: normalizeModules(raw.enabled_modules),
		created_at: raw.created_at,
		updated_at: raw.updated_at
	};
}

const meCache = new Map<string, { until: number; user: SessionUser }>();

export async function fetchSessionUser(token: string): Promise<SessionUser | null> {
	const hit = meCache.get(token);
	if (hit && hit.until > Date.now()) return hit.user;
	try {
		const me = await backendJson<any>(EP.auth.me, { token });
		let org = toOrganization(me.organization);
		if (!org && me.organization_id) {
			org = toOrganization(await backendJson<any>(EP.org.me, { token }).catch(() => null));
		}
		const user: SessionUser = {
			id: me.id,
			email: me.email,
			full_name: me.full_name ?? me.email,
			role: me.role,
			organization_id: me.organization_id ?? org?.id ?? null,
			is_active: me.is_active ?? true,
			last_login_at: me.last_login_at,
			organization: org
		};
		meCache.set(token, { until: Date.now() + 30_000, user });
		if (meCache.size > 500) meCache.clear();
		return user;
	} catch (e) {
		if (e instanceof BackendError) return null;
		throw e;
	}
}

export function invalidateUserCache(token?: string | null) {
	if (token) meCache.delete(token);
}
