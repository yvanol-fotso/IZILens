import { createApi } from '$lib/server/api';
import { EP } from '$lib/server/endpoints';
import { requirePermission } from '$lib/server/guards';
import type { AuditLog } from '$lib/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'audit:read');
	const page = Math.max(1, Number(event.url.searchParams.get('page') || 1));
	const logs = await createApi(event).paged<AuditLog>(EP.audit, {}, page, 25);
	logs.items.sort((a, b) => b.created_at.localeCompare(a.created_at));
	return { logs };
};
