import { createHash, randomBytes } from 'node:crypto';
import { authConfig } from './config';
import { BackendError } from '../backend';
import { decodeJwt } from './session';

export interface OidcProvider {
	id: string;
	authorizationEndpoint: string;
	tokenEndpoint: string;
	scopes: string[];
	clientId: string;
	clientSecret: string;
	redirectUri: string;
}

/** Pour ajouter Microsoft, Apple… : ajoutez un `case` ici, le reste est générique. */
export function getProvider(id: string, origin: string): OidcProvider | null {
	switch (id) {
		case 'google': {
			const g = authConfig.google;
			if (!authConfig.googleConfigured) return null;
			return {
				id,
				authorizationEndpoint: 'https://accounts.google.com/o/oauth2/v2/auth',
				tokenEndpoint: 'https://oauth2.googleapis.com/token',
				scopes: ['openid', 'email', 'profile'],
				clientId: g.clientId,
				clientSecret: g.clientSecret,
				redirectUri: g.redirectUri || `${origin}${authConfig.paths.oauth}`
			};
		}
		default:
			return null;
	}
}

export const randomToken = (bytes = 16) => randomBytes(bytes).toString('base64url');

export function createPkce() {
	const verifier = randomBytes(32).toString('base64url');
	const challenge = createHash('sha256').update(verifier).digest('base64url');
	return { verifier, challenge };
}

export async function exchangeCode(provider: OidcProvider, code: string, verifier: string) {
	let res: Response;
	try {
		res = await fetch(provider.tokenEndpoint, {
			method: 'POST',
			headers: { 'content-type': 'application/x-www-form-urlencoded' },
			body: new URLSearchParams({
				grant_type: 'authorization_code',
				code,
				code_verifier: verifier,
				client_id: provider.clientId,
				client_secret: provider.clientSecret,
				redirect_uri: provider.redirectUri
			})
		});
	} catch {
		throw new BackendError(503, 'oidc_unreachable');
	}
	const data = (await res.json().catch(() => ({}))) as { id_token?: string; error?: string };
	if (!res.ok || !data.id_token) throw new BackendError(400, data.error ?? 'oidc_exchange_failed');
	return data as { id_token: string };
}

/** Lecture des claims (la signature est vérifiée par le backend lors de l'échange). */
export const idTokenClaims = (idToken: string) => decodeJwt<{ nonce?: string; email?: string; email_verified?: boolean }>(idToken);
