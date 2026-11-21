import { createApi } from '$lib/server/api';
import { buildStats } from '$lib/server/analytics';
import { EP } from '$lib/server/endpoints';
import { requirePermission } from '$lib/server/guards';
import type { KycCase } from '$lib/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'cases:read');
	const cases = await createApi(event).list<KycCase>(EP.kyc.cases, { page_size: 200, limit: 200 });
	return { stats: buildStats(cases, 30) };
};
