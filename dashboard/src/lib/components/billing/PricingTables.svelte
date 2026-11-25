<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { DEFAULT_PRICING_GRID, type Plan } from '$lib/config/pricing';
	import { computeInvoice } from '$lib/utils/billing';
	import { Card, Button } from '$lib/components/shared';
	import { Check } from '@lucide/svelte';

	let { data = DEFAULT_PRICING_GRID, currentPlan = 'starter' as Plan, showSimulator = true } = $props();
	
	const i18n = getI18n();
	const { t } = i18n;
	const plans: Plan[] = ['starter', 'business', 'enterprise'];
	const currencies = ['CAD', 'USD', 'EUR', 'XOF', 'XAF'];
	
	let selectedCurrency = $state('CAD');
	let sim = $state({ plan: 'business' as Plan, cycle: 'monthly' as 'monthly' | 'annual', kyc: 100, kyb: 10, biometrics: 50, monitoring: true, integrationFee: false });

	const money = (v: number) => new Intl.NumberFormat(i18n.locale === 'fr' ? 'fr-CA' : 'en-CA', { 
		style: 'currency', 
		currency: selectedCurrency, 
		maximumFractionDigits: ['XOF', 'XAF'].includes(selectedCurrency) ? 0 : 0 
	}).format(v);

	const preview = $derived(computeInvoice(data, {
		plan: sim.plan, currency: selectedCurrency, cycle: sim.cycle,
		quantities: { kyc: sim.kyc, kyb: sim.kyb, biometrics: sim.biometrics },
		monitoring: sim.monitoring, integrationFee: sim.integrationFee
	}));

	const getPrice = (plan: Plan) => {
		const p = data.plans[plan];
		if (!p) return 0;
		return sim.cycle === 'annual' ? (p.annual?.[selectedCurrency] ?? p.monthly[selectedCurrency] * 12) : p.monthly[selectedCurrency];
	};
</script>

<div class="pricing-section">
	<div class="header-controls">
		<label>
			<span>{t('rx.f.currency')}</span>
			<select bind:value={selectedCurrency}>
				{#each currencies as c}<option>{c}</option>{/each}
			</select>
		</label>
		<label>
			<span>{t('rx.f.billing_cycle')}</span>
			<select bind:value={sim.cycle}>
				<option value="monthly">{t('rx.o.monthly')}</option>
				<option value="annual">{t('rx.o.annual')}</option>
			</select>
		</label>
	</div>

	<div class="plans-grid">
		{#each plans as plan (plan)}
			<Card class="plan-card {plan === 'business' ? 'popular' : ''}">
				<!-- Badge complètement retiré -->
				
				<h3>{t(`rx.o.${plan}`)}</h3>
				<div class="price">
					<strong>{money(getPrice(plan))}</strong>
					<span>/{sim.cycle === 'annual' ? t('marketing.pricing.perYear') : t('marketing.pricing.perMonth')}</span>
				</div>
				<ul class="features">
					<li><Check size={16} /> {sim.kyc} {t('rx.o.kyc')} {t('marketing.pricing.included')}</li>
					<li><Check size={16} /> {sim.kyb} {t('rx.o.kyb')} {t('marketing.pricing.included')}</li>
					<li><Check size={16} /> {sim.biometrics} {t('rx.o.biometrics')} {t('marketing.pricing.included')}</li>
					{#if plan === 'enterprise'}<li><Check size={16} /> {t('adm.pricing.minimum')} : {money(data.plans[plan].minimum_commitment?.[selectedCurrency] ?? 0)}</li>{/if}
				</ul>
				<Button href="/register" variant={plan === 'business' ? 'brand' : 'outline'} block>
					{plan === 'enterprise' ? t('marketing.pricing.contact') : t('marketing.pricing.start')}
				</Button>
			</Card>
		{/each}
	</div>

	{#if showSimulator}
		<Card class="simulator" title={t('adm.pricing.simulator')}>
			<div class="sim-grid">
				<div class="sim-inputs">
					<label>{t('rx.f.plan')}
						<select bind:value={sim.plan}>{#each plans as p}<option value={p}>{t(`rx.o.${p}`)}</option>{/each}</select>
					</label>
					<label>{t('rx.o.kyc')} ({t('adm.pricing.qty')}) <input type="number" min="0" bind:value={sim.kyc} /></label>
					<label>{t('rx.o.kyb')} ({t('adm.pricing.qty')}) <input type="number" min="0" bind:value={sim.kyb} /></label>
					<label>{t('rx.o.biometrics')} ({t('adm.pricing.qty')}) <input type="number" min="0" bind:value={sim.biometrics} /></label>
					<label class="chk"><input type="checkbox" bind:checked={sim.monitoring} /> {t('rx.o.monitoring')}</label>
				</div>
				<div class="sim-results">
					<div class="row"><span>{t('rx.f.subscription_amount')}</span><strong>{money(preview.subscription)}</strong></div>
					<div class="row"><span>{t('rx.f.consumption_amount')}</span><strong>{money(preview.consumptionTotal)}</strong></div>
					{#if preview.options > 0}<div class="row"><span>{t('rx.f.options_amount')}</span><strong>{money(preview.options)}</strong></div>{/if}
					<div class="row total"><span>{t('rx.f.total')}</span><strong>{money(preview.total)}</strong></div>
					{#if preview.minimumApplied}<small class="warn">{t('adm.pricing.minApplied')}</small>{/if}
				</div>
			</div>
		</Card>
	{/if}
</div>

<style lang="scss">
	.pricing-section { padding: 2rem 0; }
	.header-controls { display: flex; justify-content: center; gap: 1rem; margin-bottom: 2rem; }
	.header-controls label { display: flex; flex-direction: column; font-size: var(--fs-sm); font-weight: 700; gap: 0.3rem; }
	.header-controls select { padding: 0.5rem 1rem; border-radius: var(--radius); border: 1px solid var(--border-strong); background: var(--surface); }
	
	.plans-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 3rem; align-items: stretch; }
	
	/* La classe .popular est conservée juste pour la bordure active */
	.plan-card { display: flex; flex-direction: column; gap: 1rem; position: relative; }
	:global(.plan-card.popular) { border: 2px solid var(--primary); box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12); }
	
	.plan-card h3 { margin: 0; font-size: var(--fs-xl); }
	.price { margin: 1rem 0; }
	.price strong { font-size: 2.5rem; font-weight: 800; letter-spacing: -0.03em; }
	.price span { color: var(--fg-muted); font-size: var(--fs-sm); }
	.features { list-style: none; padding: 0; margin: 0 0 1.5rem 0; display: grid; gap: 0.6rem; }
	.features li { display: flex; align-items: center; gap: 0.5rem; font-size: var(--fs-sm); color: var(--fg-muted); }
	
	.sim-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
	.sim-inputs { display: grid; gap: 1rem; }
	.sim-inputs label { display: flex; flex-direction: column; gap: 0.3rem; font-size: var(--fs-sm); font-weight: 700; }
	.sim-inputs input[type="number"], .sim-inputs select { padding: 0.6rem; border: 1px solid var(--border-strong); border-radius: var(--radius); }
	.chk { flex-direction: row !important; align-items: center; }
	
	.sim-results { background: var(--surface-2); padding: 1.5rem; border-radius: var(--radius-lg); display: flex; flex-direction: column; gap: 0.5rem; }
	.row { display: flex; justify-content: space-between; font-size: var(--fs-sm); }
	.row.total { border-top: 2px solid var(--border); padding-top: 0.5rem; margin-top: 0.5rem; font-size: var(--fs-lg); font-weight: 800; }
	.warn { color: var(--warning); font-size: var(--fs-xs); margin-top: 0.5rem; display: block; }

	@media (max-width: 768px) {
		.sim-grid { grid-template-columns: 1fr; }
	}
</style>