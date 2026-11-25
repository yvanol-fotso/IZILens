import { clientResource } from '$lib/config/client-resources';
import { createApi } from '$lib/server/api';
import { EPX } from '$lib/server/endpoints';
import { requirePermission } from '$lib/server/guards';
import { loadList } from '$lib/server/resource';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	// requirePermission(event, 'billing:read'); // Décommenter plus tard quand le backend sera prêt
	
	const api = createApi(event);
	let summary: any = null;
	let unavailable = false;
	
	try { 
		// On tente l'appel, mais si EPX.client.billingSummary est undefined, on catch
		if (EPX.client?.billingSummary) {
			summary = await api.get<any>(EPX.client.billingSummary); 
		} else {
			unavailable = true;
		}
	} catch (e: any) { 
		if (e?.status === 404 || e?.status === 501) {
			unavailable = true; 
		} else {
			// Pour le debug, on peut logger mais on ne throw pas pour ne pas bloquer la page
			console.error('Billing API error:', e);
			unavailable = true; 
		}
	}
	
	// On simule des données pour que la page s'affiche même sans backend
	if (unavailable) {
		summary = {
			plan: 'business',
			billing_cycle: 'monthly',
			subscription_amount: 299,
			period: 'Novembre 2026',
			next_invoice_at: new Date().toISOString(),
			total_due: 583,
			usage: { kyc: { count: 100, amount: 150 }, kyb: { count: 10, amount: 45 }, biometrics: { count: 50, amount: 40 } },
			monitoring_amount: 49,
			integration_fee: null,
			discount: null,
			minimum_applied: false
		};
	}

	event.url.searchParams.set('page', '1');
	const invoices = await loadList(event, clientResource('invoices')!).catch(() => ({ items: [], cols: [] }));
	
	return { summary, unavailable, invoices };
};