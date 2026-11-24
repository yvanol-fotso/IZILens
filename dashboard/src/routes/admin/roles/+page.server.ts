import { fail } from '@sveltejs/kit';
import { ALL_PERMISSIONS, STAFF_ROLES, permissionsOf } from '$lib/config/permissions';
import { actionError, createApi } from '$lib/server/api';
import { backendJson } from '$lib/server/backend';
import { EPX } from '$lib/server/endpoints';
import { requirePermission } from '$lib/server/guards';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'adm:roles');
	const api = createApi(event);
	const remote = await api.safe(api.list<{ role: string; permissions: string[] }>(EPX.admin.roles), []);
	const map = Object.fromEntries(remote.map((r) => [r.role, r.permissions]));
	// Valeurs par défaut du front tant que le backend ne fournit pas la matrice (`fromBackend:false`).
	const roles = STAFF_ROLES.map((r) => ({ role: r, permissions: (map[r] ?? permissionsOf(r)).filter((p) => (ALL_PERMISSIONS as string[]).includes(p)) }));
	return { roles, permissions: ALL_PERMISSIONS.filter((p) => p.startsWith('adm:')), fromBackend: remote.length > 0 };
};

export const actions: Actions = {
	save: async (event) => {
		requirePermission(event, 'adm:roles');
		const fd = await event.request.formData();
		const role = String(fd.get('role'));
		if (role === 'super_admin' || !(STAFF_ROLES as string[]).includes(role)) return fail(400, { ok: false, message: 'errors.forbidden' });
		const permissions = fd.getAll('permissions').map(String);
		const reason = String(fd.get('reason') ?? '').trim();
		const code = String(fd.get('step_up_code') ?? '').trim();
		if (!reason || !/^\d{6}$/.test(code)) return fail(400, { ok: false, role, errors: { reason: reason ? '' : 'contact.errors.required', step_up_code: /^\d{6}$/.test(code) ? '' : 'auth.errors.required' } });
		try {
			await backendJson(`${EPX.admin.roles}/${role}`, { method: 'PUT', token: event.locals.accessToken, json: { permissions, reason }, headers: { 'x-step-up-code': code } });
		} catch (e) { return fail(400, { ok: false, role, message: actionError(e).message }); }
		return { ok: true, role };
	}
};
