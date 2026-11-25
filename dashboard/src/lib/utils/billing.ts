export type Plan = 'starter' | 'business' | 'enterprise';
export type Service = 'kyc' | 'kyb' | 'biometrics';

export interface PriceGrid {
	plans: Record<Plan, { monthly: Record<string, number>; annual?: Record<string, number>; minimum_commitment?: Record<string, number> }>;
	usage: Record<Service, Record<string, number>>;
	options: { monitoring_monthly: Record<string, number> };
	integration_fee: { enabled: boolean; amounts: Record<string, number> };
}

export interface InvoiceInput {
	plan: Plan;
	currency: string;
	cycle: 'monthly' | 'annual';
	quantities: Record<Service, number>;
	monitoring: boolean;
	integrationFee: boolean;
	discountPercent?: number;
}

export interface InvoicePreview {
	subscription: number;
	consumption: Record<Service, number>;
	consumptionTotal: number;
	options: number;
	integrationFee: number;
	discount: number;
	computed: number;
	minimum: number;
	minimumApplied: boolean;
	total: number;
}

const n = (v: number | undefined) => (typeof v === 'number' && !Number.isNaN(v) ? v : 0);
const round = (v: number) => Math.round(v * 100) / 100;

export function computeInvoice(grid: PriceGrid, i: InvoiceInput): InvoicePreview {
	if (!grid || !grid.plans) grid = { plans: {} as any, usage: {} as any, options: { monitoring_monthly: {} }, integration_fee: { enabled: false, amounts: {} } };
	
	const plan = grid.plans[i.plan] || { monthly: {} };
	const monthlyPrice = n(plan.monthly[i.currency]);
	
	const subscription = n(
		i.cycle === 'annual' 
			? (plan.annual?.[i.currency] ?? monthlyPrice * 12) / 12 
			: monthlyPrice
	);

	const consumption = Object.fromEntries(
		(['kyc', 'kyb', 'biometrics'] as Service[]).map((s) => [
			s, 
			round(n(i.quantities[s]) * n(grid.usage[s]?.[i.currency]))
		])
	) as Record<Service, number>;

	const consumptionTotal = round(Object.values(consumption).reduce((a, b) => a + b, 0));
	const options = i.monitoring ? n(grid.options.monitoring_monthly[i.currency]) : 0;
	const integrationFee = i.integrationFee && grid.integration_fee?.enabled ? n(grid.integration_fee.amounts[i.currency]) : 0;
	const gross = subscription + consumptionTotal + options;
	const discount = round(((gross + integrationFee) * n(i.discountPercent)) / 100);
	const computed = round(gross + integrationFee - discount);
	const minimum = i.plan === 'enterprise' ? n(plan.minimum_commitment?.[i.currency]) : 0;
	const minimumApplied = minimum > 0 && computed < minimum;

	return { 
		subscription: round(subscription), 
		consumption, 
		consumptionTotal, 
		options, 
		integrationFee, 
		discount, 
		computed, 
		minimum, 
		minimumApplied, 
		total: minimumApplied ? minimum : computed 
	};
}