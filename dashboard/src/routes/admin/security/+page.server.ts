import { ADMIN_RESOURCES } from '$lib/config/admin-resources';
import { createApi } from '$lib/server/api';
import { EPX } from '$lib/server/endpoints';
import { requirePermission } from '$lib/server/guards';
import { loadList, runAction } from '$lib/server/resource';
import type { Actions, PageServerLoad } from './$types';

const sessions = ADMIN_RESOURCES.find((r) => r.key === 'sessions')!;
const events = ADMIN_RESOURCES.find((r) => r.key === 'security-events')!;

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'adm:security');
	const api = createApi(event);
	const overview = await api.safe(api.get<Record<string, number>>(EPX.admin.securityOverview), null as any);
	return { overview, sessions: await loadList(event, sessions), events: await loadList(event, events) };
};
export const actions: Actions = { run: (event) => runAction(event, sessions, null) };
