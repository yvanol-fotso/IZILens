import { fail } from '@sveltejs/kit';
import { ASSIGNABLE_ROLES } from '$lib/config/permissions';
import { actionError, createApi } from '$lib/server/api';
import { EP } from '$lib/server/endpoints';
import { requirePermission } from '$lib/server/guards';
import type { UserRecord } from '$lib/types';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'users:manage');
	return { members: await createApi(event).list<UserRecord>(EP.users.list) };
};

export const actions: Actions = {
	invite: async (event) => {
		requirePermission(event, 'users:manage');
		const d = await event.request.formData();
		const email = String(d.get('email') ?? '').trim().toLowerCase();
		const full_name = String(d.get('full_name') ?? '').trim();
		const role = String(d.get('role'));
		const password = String(d.get('password') ?? '');
		const errors: Record<string, string> = {};
		if (!full_name) errors.full_name = 'auth.errors.required';
		if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errors.email = 'auth.errors.email';
		if (password.length < 12) errors.password = 'auth.errors.passwordShort';
		if (!(ASSIGNABLE_ROLES as string[]).includes(role)) errors.role = 'auth.errors.required';
		if (Object.keys(errors).length) return fail(400, { ok: false, errors });
		try {
			await createApi(event).post(EP.users.list, { email, full_name, role, password });
		} catch (e) {
			return fail(400, { ok: false, message: actionError(e).message });
		}
		return { ok: true, invited: true };
	},
	update: async (event) => {
		requirePermission(event, 'users:manage');
		const d = await event.request.formData();
		const id = String(d.get('id'));
		const body: Record<string, unknown> = {};
		if (d.has('role')) body.role = String(d.get('role'));
		if (d.has('is_active')) body.is_active = d.get('is_active') === 'true';
		try {
			await createApi(event).patch(EP.users.one(id), body);
		} catch (e) {
			return fail(400, { ok: false, message: actionError(e).message });
		}
		return { ok: true, updated: true };
	}
};
