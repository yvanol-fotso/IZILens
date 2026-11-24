import { error } from '@sveltejs/kit';
import { clientResource } from '$lib/config/client-resources';
import { requirePermission } from '$lib/server/guards';
import { createRecord, loadList, runAction } from '$lib/server/resource';
import type { Actions, PageServerLoad } from './$types';

const def = (key: string) => clientResource(key) ?? error(404, { message: 'not_found', code: 'not_found' });

export const load: PageServerLoad = async (event) => {
	const d = def(event.params.resource);
	requirePermission(event, d.read);
	return { key: d.key, list: await loadList(event, d) };
};

export const actions: Actions = {
	create: (event) => createRecord(event, def(event.params.resource)),
	run: (event) => runAction(event, def(event.params.resource), null)
};
