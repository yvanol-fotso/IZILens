import { requirePermission } from '$lib/server/guards';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = (event) => {
	requirePermission(event, 'adm:reports');
	return {};
};
