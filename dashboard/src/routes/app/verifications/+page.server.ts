import { createApi } from '$lib/server/api';
import { EP } from '$lib/server/endpoints';
import { requirePermission } from '$lib/server/guards';
import type { KycCase } from '$lib/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'cases:read');
	const api = createApi(event);
	const sp = event.url.searchParams;
	const page = Math.max(1, Number(sp.get('page') || 1));
	const pageSize = 15;
	const filters = { status: sp.get('status') ?? '', risk_level: sp.get('risk_level') ?? '', search: (sp.get('search') ?? '').trim() };
	const q = filters.search.toLowerCase();

	const cases = await api.paged<KycCase>(
		EP.kyc.cases,
		{ status: filters.status, risk_level: filters.risk_level, search: filters.search },
		page,
		pageSize,
		// Filtre de secours si le backend renvoie un simple tableau non filtré.
		(c) => (!filters.status || c.status === filters.status) && (!filters.risk_level || c.risk_level === filters.risk_level) && (!q || `${c.reference} ${c.id}`.toLowerCase().includes(q))
	);
	cases.items.sort((a, b) => b.created_at.localeCompare(a.created_at));
	return { cases, filters };
};
