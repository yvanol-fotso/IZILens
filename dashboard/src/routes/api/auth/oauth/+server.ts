import { redirect, type RequestEvent, type RequestHandler } from '@sveltejs/kit';
import { BackendError, backendJson } from '$lib/server/backend';
import { EP } from '$lib/server/endpoints';
import { createPkce, exchangeCode, getProvider, idTokenClaims, randomToken } from '$lib/server/auth/google';
import { postLoginPath, safeNext } from '$lib/server/auth/policy';
import { OAUTH_COOKIE, oauthCookieOptions, setSession } from '$lib/server/auth/session';
import type { TokenPair } from '$lib/types/auth';

/**
 * Point d'entrée OIDC unique : /api/auth/oauth
 *  - GET ?provider=google[&next=/app]  → redirige vers le fournisseur (code + PKCE + state + nonce)
 *  - GET ?code=…&state=…               → retour du fournisseur : échange le code, puis le backend
 *    FastAPI vérifie l'id_token et émet SES jetons JWT (le dashboard ne signe rien).
 */
export const GET: RequestHandler = (event) => {
	const { url } = event;
	return url.searchParams.has('code') || url.searchParams.has('error') ? callback(event) : start(event);
};

function start({ url, cookies }: RequestEvent): never {
	const providerId = url.searchParams.get('provider') ?? 'google';
	const provider = getProvider(providerId, url.origin);
	if (!provider) redirect(303, '/login?error=oauth_unavailable');

	const state = randomToken();
	const nonce = randomToken();
	const { verifier, challenge } = createPkce();
	cookies.set(OAUTH_COOKIE, JSON.stringify({ state, nonce, verifier, provider: provider.id, next: safeNext(url.searchParams.get('next'), '') }), oauthCookieOptions());

	const auth = new URL(provider.authorizationEndpoint);
	auth.search = new URLSearchParams({
		client_id: provider.clientId,
		redirect_uri: provider.redirectUri,
		response_type: 'code',
		scope: provider.scopes.join(' '),
		state,
		nonce,
		code_challenge: challenge,
		code_challenge_method: 'S256',
		prompt: 'select_account'
	}).toString();
	redirect(302, auth.toString());
}

async function callback({ url, cookies }: RequestEvent): Promise<never> {
	const raw = cookies.get(OAUTH_COOKIE);
	cookies.delete(OAUTH_COOKIE, { path: '/api/auth/oauth' });

	let saved: { state: string; nonce: string; verifier: string; next: string; provider: string } | null = null;
	try {
		saved = raw ? JSON.parse(raw) : null;
	} catch {
		saved = null;
	}
	const provider = saved ? getProvider(saved.provider, url.origin) : null;
	const code = url.searchParams.get('code');

	if (url.searchParams.get('error') || !provider || !saved || !code || saved.state !== url.searchParams.get('state')) {
		redirect(303, '/login?error=oauth_failed');
	}

	let tokens: TokenPair;
	try {
		const { id_token } = await exchangeCode(provider, code, saved.verifier);
		if (idTokenClaims(id_token)?.nonce !== saved.nonce) redirect(303, '/login?error=oauth_failed');
		tokens = await backendJson<TokenPair>(EP.auth.oauth(provider.id), { method: 'POST', json: { id_token, nonce: saved.nonce } });
	} catch (e) {
		if (e instanceof BackendError && (e.status === 403 || e.status === 404)) redirect(303, '/login?error=oauth_denied');
		if (e instanceof BackendError && e.status === 503) redirect(303, '/login?error=unreachable');
		redirect(303, '/login?error=oauth_failed');
	}

	setSession(cookies, tokens);
	redirect(303, postLoginPath(null, saved.next || null));
}
