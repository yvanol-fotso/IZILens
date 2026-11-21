import { json, type RequestHandler } from '@sveltejs/kit';
import { BackendError } from '$lib/server/backend';
import { loginWithPassword } from '$lib/server/auth/service';
import { setSession } from '$lib/server/auth/session';

/** Connexion JWT programmatique (email + mot de passe). Les pages utilisent l'action de /login. */
export const POST: RequestHandler = async ({ request, cookies }) => {
	const { email, password } = await request.json().catch(() => ({}));
	if (!email || !password) return json({ detail: 'missing_credentials' }, { status: 400 });
	try {
		setSession(cookies, await loginWithPassword(String(email), String(password)));
		return json({ ok: true });
	} catch (e) {
		if (e instanceof BackendError) return json({ detail: e.detail }, { status: e.status });
		throw e;
	}
};
