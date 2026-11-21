import { fail } from '@sveltejs/kit';
import { actionError, createApi } from '$lib/server/api';
import { toOrganization } from '$lib/server/auth/service';
import { EP } from '$lib/server/endpoints';
import { requireSuperAdmin } from '$lib/server/guards';
import type { UserRecord } from '$lib/types';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	const api = createApi(event);
	const org = toOrganization(await api.get<any>(EP.org.one(event.params.id)));
	if (!org) return { tenant: null as never, members: [] };
	const all = await api.safe(api.list<UserRecord>(EP.users.list), []);
	return { tenant: org, members: all.filter((u) => u.organization_id === org.id) };
};

export const actions: Actions = {
	modules: async (event) => {
		requireSuperAdmin(event);
		const modules = (await event.request.formData()).getAll('modules').map(String);
		try {
			await createApi(event).patch(EP.org.one(event.params.id), { enabled_modules: modules });
		} catch (e) {
			return fail(400, { ok: false, message: actionError(e).message });
		}
		return { ok: true };
	},
	status: async (event) => {
		requireSuperAdmin(event);
		const active = (await event.request.formData()).get('is_active') === 'true';
		try {
			await createApi(event).patch(EP.org.one(event.params.id), { is_active: active });
		} catch (e) {
			return fail(400, { ok: false, message: actionError(e).message });
		}
		return { ok: true };
	}
};
