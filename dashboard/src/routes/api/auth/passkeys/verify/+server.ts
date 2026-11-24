import { json, type RequestHandler } from '@sveltejs/kit';
import { BackendError, backendJson } from '$lib/server/backend';
import { EPX } from '$lib/server/endpoints';

/** Étape 2 : transmet la réponse de l'authentificateur ; le backend vérifie et enregistre la passkey. */
export const POST: RequestHandler = async ({ locals, request }) => {
	if (!locals.accessToken) return json({ detail: 'Unauthorized' }, { status: 401 });
	try { return json(await backendJson(EPX.auth.passkeyVerify, { method: 'POST', token: locals.accessToken, json: await request.json() })); }
	catch (e) { return json({ detail: e instanceof BackendError ? e.detail : 'error' }, { status: e instanceof BackendError ? e.status : 500 }); }
};
