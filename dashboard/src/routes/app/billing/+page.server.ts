import { clientResource } from '$lib/config/client-resources';
import { createApi } from '$lib/server/api';
import { EPX } from '$lib/server/endpoints';
import { requirePermission } from '$lib/server/guards';
import { loadList } from '$lib/server/resource';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'billing:read');
	const api = createApi(event);
	let summary: any = null;
	let unavailable = false;
	try { summary = await api.get<any>(EPX.client.billingSummary); } catch (e: any) { if (e?.status === 404 || e?.status === 501) unavailable = true; else throw e; }
	event.url.searchParams.set('page', '1');
	const invoices = await loadList(event, clientResource('invoices')!);
	return { summary, unavailable, invoices };
};
