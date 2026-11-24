import { error } from '@sveltejs/kit';
import { adminResource } from '$lib/config/admin-resources';
import { createApi } from '$lib/server/api';
import { requirePermission } from '$lib/server/guards';
import { loadDetail, runAction, updateRecord } from '$lib/server/resource';
import type { Actions, PageServerLoad } from './$types';

const def = (key: string) => {
	const d = adminResource(key);
	if (!d || d.detail === false) error(404, { message: 'not_found', code: 'not_found' });
	return d;
};

export const load: PageServerLoad = async (event) => {
	const d = def(event.params.resource);
	requirePermission(event, d.read);
	const api = createApi(event);
	const needsStaff = d.actions?.some((a) => a.fields?.some((f) => f.type === 'staff'));
	const [detail, staff] = await Promise.all([loadDetail(event, d, event.params.id), needsStaff ? api.safe(api.list<{ id: string; full_name: string }>('/admin/staff'), []) : Promise.resolve([])]);
	return { key: d.key, ...detail, staff };
};

export const actions: Actions = {
	run: (event) => runAction(event, def(event.params.resource), event.params.id),
	update: (event) => updateRecord(event, def(event.params.resource), event.params.id)
};
