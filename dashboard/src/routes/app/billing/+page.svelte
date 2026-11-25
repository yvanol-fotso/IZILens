<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { PageHeader, Card, Button } from '$lib/components/shared';
	// On importe tout depuis l'index
	import { UsageMeter, InvoiceTable, PricingTables } from '$lib/components/billing';
	import { DEFAULT_PRICING_GRID } from '$lib/config/pricing';

	// MOCK DATA
	const mockSubscription = {
		plan: 'business',
		status: 'active',
		period_end: '2026-12-01',
		usage: {
			kyc: { count: 45, quota: 100 },
			kyb: { count: 2, quota: 10 },
			biometrics: { count: 55, quota: 50 }
		}
	};

	const mockInvoices = [
		{ id: 'INV-2026-001', amount: 583.00, currency: 'CAD', status: 'paid', date: '2026-10-01' },
		{ id: 'INV-2026-002', amount: 299.00, currency: 'CAD', status: 'open', date: '2026-11-01' }
	];
	
	const { t } = getI18n();
</script>

<PageHeader title={t('cli.billing.title')} subtitle={t('cli.billing.subtitle')} />

<div class="dashboard-grid">
	<div class="col-main">
		<Card title={t('cli.billing.plan') || 'Votre Plan'} class="plan-card">
			<div class="plan-header">
				<div>
					<h3 class="plan-name">{t(`rx.o.${mockSubscription.plan}`)}</h3>
					<p class="plan-status">{t('rx.o.active')} · {t('cli.billing.next')} : {mockSubscription.period_end}</p>
				</div>
				<Button variant="outline" size="sm" href="#pricing">{t('cli.billing.changePlan') || 'Changer de plan'}</Button>
			</div>
		</Card>

		<Card title={t('cli.billing.consumption') || 'Consommation du mois'} class="usage-section">
			<UsageMeter usage={mockSubscription.usage} />
		</Card>

		<Card title={t('rx.r.invoices.title') || 'Historique des factures'} padded={false}>
			<InvoiceTable invoices={mockInvoices} />
		</Card>
	</div>
</div>

<div id="pricing" style="margin-top: 4rem;">
	<PageHeader title={t('marketing.pricing.title')} subtitle={t('marketing.pricing.subtitle')} />
	<PricingTables data={DEFAULT_PRICING_GRID} currentPlan={mockSubscription.plan} showSimulator={false} />
</div>

<style lang="scss">
	.dashboard-grid { display: flex; flex-direction: column; gap: 1.5rem; }
	.col-main { display: grid; gap: 1.5rem; }
	
	.plan-card { background: linear-gradient(135deg, var(--surface) 0%, var(--surface-2) 100%); border: 1px solid var(--primary); }
	.plan-header { display: flex; justify-content: space-between; align-items: center; }
	.plan-name { font-size: var(--fs-2xl); font-weight: 800; margin: 0; color: var(--primary); }
	.plan-status { color: var(--fg-muted); font-size: var(--fs-sm); margin-top: 0.2rem; }
</style>