import { fail } from '@sveltejs/kit';
import { actionError, createApi } from '$lib/server/api';
import { toOrganization } from '$lib/server/auth/service';
import { EP } from '$lib/server/endpoints';
import { requireSuperAdmin } from '$lib/server/guards';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	const raw = await createApi(event).list<any>(EP.org.list);
	return { tenants: raw.map(toOrganization).filter((o): o is NonNullable<typeof o> => !!o) };
};

export const actions: Actions = {
	create: async (event) => {
		requireSuperAdmin(event);
		const d = await event.request.formData();
		const name = String(d.get('name') ?? '').trim();
		const slug = String(d.get('slug') ?? '').trim().toLowerCase();
		const admin_email = String(d.get('admin_email') ?? '').trim().toLowerCase();
		const enabled_modules = d.getAll('modules').map(String);
		const errors: Record<string, string> = {};
		if (!name) errors.name = 'auth.errors.required';
		if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(slug)) errors.slug = 'admin.tenants.slugHint';
		if (admin_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(admin_email)) errors.admin_email = 'auth.errors.email';
		if (Object.keys(errors).length) return fail(400, { ok: false, errors });
		try {
			await createApi(event).post(EP.org.list, { name, slug, enabled_modules, ...(admin_email ? { admin_email } : {}) });
		} catch (e) {
			return fail(400, { ok: false, message: actionError(e).message });
		}
		return { ok: true, created: true };
	}
};
