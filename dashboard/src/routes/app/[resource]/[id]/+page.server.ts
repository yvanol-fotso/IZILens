import { error } from '@sveltejs/kit';
import { clientResource } from '$lib/config/client-resources';
import { requirePermission } from '$lib/server/guards';
import { loadDetail, runAction, updateRecord } from '$lib/server/resource';
import type { Actions, PageServerLoad } from './$types';

const def = (key: string) => {
	const d = clientResource(key);
	if (!d || d.detail === false) error(404, { message: 'not_found', code: 'not_found' });
	return d;
};

export const load: PageServerLoad = async (event) => {
	const d = def(event.params.resource);
	requirePermission(event, d.read);
	return { key: d.key, ...(await loadDetail(event, d, event.params.id)) };
};

export const actions: Actions = {
	run: (event) => runAction(event, def(event.params.resource), event.params.id),
	update: (event) => updateRecord(event, def(event.params.resource), event.params.id)
};
