import { createApi } from '$lib/server/api';
import { buildStats } from '$lib/server/analytics';
import { EP } from '$lib/server/endpoints';
import { can } from '$lib/config/permissions';
import type { KycCase } from '$lib/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	const api = createApi(event);
	const user = event.locals.user!;
	const cases = can(user.role, 'cases:read') ? await api.list<KycCase>(EP.kyc.cases, { page_size: 200, limit: 200 }) : [];
	const recent = [...cases].sort((a, b) => b.created_at.localeCompare(a.created_at)).slice(0, 6);
	return { stats: buildStats(cases), recent };
};
