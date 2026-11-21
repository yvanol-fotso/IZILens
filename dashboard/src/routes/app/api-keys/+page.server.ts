import { fail } from '@sveltejs/kit';
import { actionError, createApi } from '$lib/server/api';
import { EP } from '$lib/server/endpoints';
import { requirePermission } from '$lib/server/guards';
import type { ApiKey } from '$lib/types';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'keys:manage');
	return { keys: await createApi(event).list<ApiKey>(EP.apiKeys.list) };
};

export const actions: Actions = {
	create: async (event) => {
		requirePermission(event, 'keys:manage');
		const d = await event.request.formData();
		const name = String(d.get('name') ?? '').trim();
		const days = Number(d.get('expires_in_days') || 0);
		if (!name) return fail(400, { ok: false, message: 'auth.errors.required' });
		try {
			const created = await createApi(event).post<{ key?: string; api_key?: string; secret?: string }>(EP.apiKeys.list, { name, ...(days ? { expires_in_days: days } : {}) });
			// La clé en clair n'existe QU'ICI : elle est renvoyée une seule fois à la page, jamais stockée.
			return { ok: true, created: { name, key: created.key ?? created.api_key ?? created.secret ?? '' } };
		} catch (e) {
			return fail(400, { ok: false, message: actionError(e).message });
		}
	},
	revoke: async (event) => {
		requirePermission(event, 'keys:manage');
		const id = String((await event.request.formData()).get('id'));
		try {
			await createApi(event).del(EP.apiKeys.one(id));
		} catch (e) {
			return fail(400, { ok: false, message: actionError(e).message });
		}
		return { ok: true, revoked: true };
	}
};
