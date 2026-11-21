import { fail, redirect } from '@sveltejs/kit';
import { BackendError, backendJson } from '$lib/server/backend';
import { EP } from '$lib/server/endpoints';
import type { Actions } from './$types';

export const actions: Actions = {
	default: async ({ request }) => {
		const d = await request.formData();
		const full_name = String(d.get('full_name') ?? '').trim();
		const email = String(d.get('email') ?? '').trim().toLowerCase();
		const password = String(d.get('password') ?? '');
		const confirm = String(d.get('confirm') ?? '');

		const errors: Record<string, string> = {};
		if (!full_name) errors.full_name = 'auth.errors.required';
		if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errors.email = 'auth.errors.email';
		if (password.length < 12) errors.password = 'auth.errors.passwordShort';
		if (confirm !== password) errors.confirm = 'auth.errors.passwordMismatch';
		if (Object.keys(errors).length) return fail(400, { ok: false, errors, values: { full_name, email } });

		try {
			await backendJson(EP.auth.register, { method: 'POST', json: { full_name, email, password } });
		} catch (e) {
			const status = e instanceof BackendError ? e.status : 500;
			return fail(status === 503 ? 503 : 400, { ok: false, message: status === 503 ? 'auth.errors.unreachable' : e instanceof BackendError ? e.detail : 'auth.errors.generic', values: { full_name, email } });
		}
		redirect(303, '/login?info=registered');
	}
};
