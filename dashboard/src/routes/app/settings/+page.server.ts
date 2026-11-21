import { fail } from '@sveltejs/kit';
import { actionError, createApi } from '$lib/server/api';
import { invalidateUserCache } from '$lib/server/auth/service';
import { EP } from '$lib/server/endpoints';
import type { Actions } from './$types';

export const actions: Actions = {
	profile: async (event) => {
		const full_name = String((await event.request.formData()).get('full_name') ?? '').trim();
		if (!full_name) return fail(400, { ok: false, form: 'profile', errors: { full_name: 'auth.errors.required' } });
		try {
			await createApi(event).patch(EP.users.me, { full_name });
			invalidateUserCache(event.locals.accessToken);
		} catch (e) {
			return fail(400, { ok: false, form: 'profile', message: actionError(e).message });
		}
		return { ok: true, form: 'profile' };
	},
	password: async (event) => {
		const d = await event.request.formData();
		const current_password = String(d.get('current_password') ?? '');
		const new_password = String(d.get('new_password') ?? '');
		if (!current_password) return fail(400, { ok: false, form: 'password', errors: { current_password: 'auth.errors.required' } });
		if (new_password.length < 12) return fail(400, { ok: false, form: 'password', errors: { new_password: 'auth.errors.passwordShort' } });
		try {
			await createApi(event).post(EP.auth.changePassword, { current_password, new_password });
		} catch (e) {
			return fail(400, { ok: false, form: 'password', message: actionError(e).message });
		}
		return { ok: true, form: 'password' };
	}
};
