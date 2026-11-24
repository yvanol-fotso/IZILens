import { json, type RequestHandler } from '@sveltejs/kit';
import { BackendError, backendJson } from '$lib/server/backend';
import { EPX } from '$lib/server/endpoints';

/** Étape 1 de l'enregistrement d'une passkey : options WebAuthn fournies par le backend. */
export const POST: RequestHandler = async ({ locals }) => {
	if (!locals.accessToken) return json({ detail: 'Unauthorized' }, { status: 401 });
	try { return json(await backendJson(EPX.auth.passkeyOptions, { method: 'POST', token: locals.accessToken, json: {} })); }
	catch (e) { return json({ detail: e instanceof BackendError ? e.detail : 'error' }, { status: e instanceof BackendError ? e.status : 500 }); }
};
