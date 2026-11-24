import { fail, redirect } from '@sveltejs/kit';
import { BackendError, backendJson } from '$lib/server/backend';
import { EPX } from '$lib/server/endpoints';
import { clearMfaChallenge, getMfaChallenge } from '$lib/server/auth/mfa';
import { postLoginPath } from '$lib/server/auth/policy';
import { setSession } from '$lib/server/auth/session';
import type { TokenPair } from '$lib/types';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = ({ cookies }) => {
	if (!getMfaChallenge(cookies)) redirect(303, '/login');
	return {};
};

export const actions: Actions = {
	default: async ({ request, cookies }) => {
		const challenge = getMfaChallenge(cookies);
		if (!challenge) redirect(303, '/login');
		const code = String((await request.formData()).get('code') ?? '').replace(/\s/g, '');
		if (!/^\d{6}$/.test(code) && !/^[A-Za-z0-9-]{8,}$/.test(code)) return fail(400, { ok: false, message: 'auth.errors.invalid' });
		let tokens: TokenPair;
		try {
			// `code` = code TOTP à 6 chiffres, ou code de récupération.
			tokens = await backendJson<TokenPair>(EPX.auth.mfaVerify, { method: 'POST', json: { mfa_token: challenge.token, code } });
		} catch (e) {
			if (e instanceof BackendError && e.status === 503) return fail(503, { ok: false, message: 'auth.errors.unreachable' });
			return fail(400, { ok: false, message: 'auth.errors.invalid' });
		}
		clearMfaChallenge(cookies);
		setSession(cookies, tokens);
		redirect(303, postLoginPath(null, challenge.next || null));
	}
};
