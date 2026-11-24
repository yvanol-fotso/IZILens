import { fail, redirect } from '@sveltejs/kit';
import { BackendError } from '$lib/server/backend';
import { loginWithPassword } from '$lib/server/auth/service';
import { postLoginPath } from '$lib/server/auth/policy';
import { setSession } from '$lib/server/auth/session';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = ({ url }) => {
	const err = url.searchParams.get('error');
	const info = url.searchParams.get('info');
	return {
		next: url.searchParams.get('next') ?? '',
		notice: info === 'logged_out' ? 'auth.login.loggedOut' : info === 'registered' ? 'auth.login.registered' : err === 'session' ? 'auth.login.sessionExpired' : null,
		oauthError: err && err !== 'session' ? `auth.errors.${err}` : null
	};
};

export const actions: Actions = {
	default: async ({ request, cookies }) => {
		const data = await request.formData();
		const email = String(data.get('email') ?? '').trim().toLowerCase();
		const password = String(data.get('password') ?? '');
		const mfaCode = String(data.get('mfa_code') ?? '').trim();
		const next = String(data.get('next') ?? '');

		const errors: Record<string, string> = {};
		if (!email) errors.email = 'auth.errors.required';
		else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errors.email = 'auth.errors.email';
		if (!password) errors.password = 'auth.errors.required';
		if (Object.keys(errors).length) return fail(400, { ok: false, errors, values: { email } });

		try {
			setSession(cookies, await loginWithPassword(email, password, mfaCode || undefined));
		} catch (e) {
			const backendCode = e instanceof BackendError ? ((e.data as { error?: { code?: string } } | undefined)?.error?.code ?? '') : '';
			if (backendCode === 'MFA_REQUIRED' || backendCode === 'INVALID_MFA_CODE') {
				return fail(401, { ok: false, mfaRequired: true, message: backendCode === 'MFA_REQUIRED' ? 'auth.errors.mfaRequired' : 'auth.errors.mfaInvalid', values: { email } });
			}
			const status = e instanceof BackendError ? e.status : 500;
			const message = status === 423 || status === 429 ? 'auth.errors.locked' : status === 503 ? 'auth.errors.unreachable' : status === 401 || status === 400 || status === 422 ? 'auth.errors.invalid' : 'auth.errors.generic';
			return fail(status === 503 ? 503 : 400, { ok: false, message, values: { email } });
		}
		redirect(303, postLoginPath(null, next || null));
	}
};
