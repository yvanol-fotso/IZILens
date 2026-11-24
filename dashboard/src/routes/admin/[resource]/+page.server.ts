import { error } from '@sveltejs/kit';
import { adminResource } from '$lib/config/admin-resources';
import { requirePermission } from '$lib/server/guards';
import { createApi } from '$lib/server/api';
import { createRecord, loadList, runAction } from '$lib/server/resource';
import type { Actions, PageServerLoad } from './$types';

const def = (key: string) => adminResource(key) ?? error(404, { message: 'not_found', code: 'not_found' });
const needsStaff = (d: ReturnType<typeof def>) => !!(d.actions?.some((a) => a.fields?.some((f) => f.type === 'staff')) || d.create?.fields.some((f) => f.type === 'staff'));

export const load: PageServerLoad = async (event) => {
	const d = def(event.params.resource);
	requirePermission(event, d.read);
	const api = createApi(event);
	const [list, staff] = await Promise.all([loadList(event, d), needsStaff(d) ? api.safe(api.list<{ id: string; full_name: string }>('/admin/staff'), []) : Promise.resolve([])]);
	return { key: d.key, list, staff };
};

export const actions: Actions = {
	create: (event) => createRecord(event, def(event.params.resource)),
	run: (event) => runAction(event, def(event.params.resource), null)
};
