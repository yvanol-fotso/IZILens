import { redirect, type Handle } from '@sveltejs/kit';
import { LOCALE_COOKIE, resolveLocale } from '$lib/i18n/locales';
import { fetchSessionUser, refreshTokens } from '$lib/server/auth/service';
import { decideAccess, isProxyPath } from '$lib/server/auth/policy';
import { ACCESS_COOKIE, REFRESH_COOKIE, clearSession, isExpired, setSession } from '$lib/server/auth/session';

const THEMES = ['light', 'dark', 'system'];

export const handle: Handle = async ({ event, resolve }) => {
	const { cookies, url, request, locals } = event;

	// ── Langue & thème ──────────────────────────────────────────────────────
	locals.locale = resolveLocale(cookies.get(LOCALE_COOKIE), request.headers.get('accept-language'));
	const themeCookie = cookies.get('izi_theme');
	locals.theme = themeCookie && THEMES.includes(themeCookie) ? themeCookie : 'light';
	locals.user = null;
	locals.accessToken = null;

	// ── Session (JWT backend en cookies httpOnly, refresh transparent) ──────
	const isAsset = url.pathname.startsWith('/_app') || url.pathname === '/favicon.svg';
	if (!isAsset) {
		let access = cookies.get(ACCESS_COOKIE) ?? null;
		const refresh = cookies.get(REFRESH_COOKIE);

		if ((!access || isExpired(access)) && refresh) {
			const tokens = await refreshTokens(refresh);
			if (tokens) {
				setSession(cookies, tokens);
				access = tokens.access_token;
			} else {
				clearSession(cookies);
				access = null;
			}
		}

		if (access && !isExpired(access)) {
			locals.accessToken = access;
			// Le proxy /api/v1 n'a besoin que du jeton : on évite un aller-retour /me.
			if (!isProxyPath(url.pathname)) locals.user = await fetchSessionUser(access);
			if (!locals.user && !isProxyPath(url.pathname)) locals.accessToken = null;
		}
	}

	// ── Garde-fous de routes (politique centralisée dans auth/policy.ts) ───
	const decision = decideAccess(url.pathname, url.search, locals.user, !!locals.accessToken);
	if (decision.type === 'redirect') redirect(303, decision.to);

	const response = await resolve(event, {
		transformPageChunk: ({ html }) => html.replace('%lang%', locals.locale).replace('%theme%', locals.theme)
	});

	response.headers.set('X-Content-Type-Options', 'nosniff');
	response.headers.set('X-Frame-Options', 'DENY');
	response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
	response.headers.set('Permissions-Policy', 'camera=(self), microphone=(), geolocation=()');
	return response;
};
