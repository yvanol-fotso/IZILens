import { json, type RequestHandler } from '@sveltejs/kit';
import { refreshTokens } from '$lib/server/auth/service';
import { REFRESH_COOKIE, clearSession, setSession } from '$lib/server/auth/session';

export const POST: RequestHandler = async ({ cookies }) => {
	const refresh = cookies.get(REFRESH_COOKIE);
	const tokens = refresh ? await refreshTokens(refresh) : null;
	if (!tokens) {
		clearSession(cookies);
		return json({ ok: false }, { status: 401 });
	}
	setSession(cookies, tokens);
	return json({ ok: true });
};
