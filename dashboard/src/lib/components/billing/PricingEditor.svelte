<script lang="ts">
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { toastSuccess } from '$lib/stores/toast';
	import type { FormState } from '$lib/types';
	import { Button, Card, FormAlert, Input, Switch, Textarea } from '$lib/components/shared';
	import { computeInvoice, type PriceGrid, type Plan, type Service } from '$lib/utils/billing';
	import { DEFAULT_PRICING_GRID } from '$lib/config/pricing';

	let { pricing = DEFAULT_PRICING_GRID, currencies = ['CAD'], form = null, canWrite = false }: { pricing: any; currencies: string[]; form?: FormState | null; canWrite: boolean } = $props();
	const i18n = getI18n();
	const { t } = i18n;
	let loading = $state(false);
	const err = (k: string) => (form?.errors?.[k] ? t(form.errors[k]) : undefined);

	const plans: Plan[] = ['starter', 'business', 'enterprise'];
	const services: Service[] = ['kyc', 'kyb', 'biometrics'];
	
	// Fallback sur DEFAULT_PRICING_GRID si pricing est vide ou incomplet
	let grid = $state<PriceGrid>(structuredClone($state.snapshot(pricing) ?? DEFAULT_PRICING_GRID));
	
	for (const p of plans) {
		grid.plans[p] ??= { monthly: {}, annual: {}, minimum_commitment: {} };
		grid.plans[p].monthly ??= {};
		grid.plans[p].annual ??= {};
		grid.plans[p].minimum_commitment ??= {};
	}
	for (const s of services) grid.usage[s] ??= {};
	grid.options ??= { monitoring_monthly: {} }; 
	grid.integration_fee ??= { enabled: false, amounts: {} };

	let sim = $state({ plan: 'business' as Plan, currency: currencies[0] ?? 'CAD', cycle: 'monthly' as 'monthly' | 'annual', kyc: 0, kyb: 0, biometrics: 0, monitoring: true, integrationFee: false, discount: 0 });
	const preview = $derived(computeInvoice(grid, { plan: sim.plan, currency: sim.currency, cycle: sim.cycle, quantities: { kyc: sim.kyc, kyb: sim.kyb, biometrics: sim.biometrics }, monitoring: sim.monitoring, integrationFee: sim.integrationFee, discountPercent: sim.discount }));
	const money = (v: number) => new Intl.NumberFormat(i18n.locale === 'fr' ? 'fr-CA' : 'en-CA', { style: 'currency', currency: sim.currency, maximumFractionDigits: ['XOF', 'XAF'].includes(sim.currency) ? 0 : 2 }).format(v);
</script>

<form method="POST" action="?/save" class="stack" use:enhance={() => { loading = true; return async ({ result, update }) => { if (result.type === 'success') { toastSuccess(t('rx.ui.done')); await invalidateAll(); } await update({ reset: false }); loading = false; }; }}>
	<FormAlert {form} />
	<p class="ver">{t('adm.pricing.version')} <b>{pricing?.version ?? '—'}</b> · {t('adm.pricing.effective')} <b>{pricing?.effective_from ?? '—'}</b></p>

	{#snippet matrix(title: string, hint: string | undefined, rows: { label: string; path: string; get: Record<string, number> }[])}
		<Card {title} description={hint}>
			<div class="mx"><table>
				<thead><tr><th></th>{#each currencies as c (c)}<th>{c}</th>{/each}</tr></thead>
				<tbody>{#each rows as r (r.path)}<tr><th scope="row">{r.label}</th>{#each currencies as c (c)}<td><input type="number" step="0.01" min="0" name="p:{r.path}.{c}" bind:value={r.get[c]} disabled={!canWrite} aria-label="{r.label} {c}" /></td>{/each}</tr>{/each}</tbody>
			</table></div>
		</Card>
	{/snippet}

	{@render matrix(t('adm.pricing.subscriptions'), t('adm.pricing.currencyNote'), plans.flatMap((p) => [{ label: `${t(`rx.o.${p}`)} · ${t('rx.o.monthly')}`, path: `plans.${p}.monthly`, get: grid.plans[p].monthly }, { label: `${t(`rx.o.${p}`)} · ${t('rx.o.annual')}`, path: `plans.${p}.annual`, get: (grid.plans[p].annual ??= {}) }]))}
	{@render matrix(t('adm.pricing.enterpriseMin'), t('adm.pricing.enterpriseMinHint'), [{ label: t('rx.o.enterprise'), path: 'plans.enterprise.minimum_commitment', get: (grid.plans.enterprise.minimum_commitment ??= {}) }])}
	{@render matrix(t('adm.pricing.unit'), undefined, services.map((s) => ({ label: t(`rx.o.${s}`), path: `usage.${s}`, get: grid.usage[s] })))}
	{@render matrix(t('adm.pricing.options'), undefined, [{ label: t('rx.o.monitoring'), path: 'options.monitoring_monthly', get: grid.options.monitoring_monthly }])}
	{@render matrix(t('adm.pricing.integration'), t('adm.pricing.integrationHint'), [{ label: t('adm.pricing.integrationFee'), path: 'integration_fee.amounts', get: grid.integration_fee.amounts }])}
	<Card><Switch name="integration_enabled" label={t('adm.pricing.integrationEnabled')} bind:checked={grid.integration_fee.enabled} disabled={!canWrite} /></Card>

	{#if canWrite}
		<Card title={t('rx.ui.confirmChange')} description={t('adm.pricing.noRetro')}>
			<div class="stack">
				<Input label={t('adm.pricing.effectiveFrom')} name="effective_from" type="date" />
				<Textarea label="{t('rx.ui.reason')} *" name="reason" error={err('reason')} />
				<Input label="{t('rx.ui.stepUp')} *" name="step_up_code" inputmode="numeric" maxlength={6} autocomplete="one-time-code" hint={t('rx.ui.stepUpHint')} error={err('step_up_code')} />
				<div><Button type="submit" variant="brand" {loading}>{t('adm.pricing.publish')}</Button></div>
			</div>
		</Card>
	{/if}
</form>

<Card title={t('adm.pricing.simulator')} description={t('adm.pricing.simulatorHint')}>
	<div class="sim">
		<div class="stack">
			<label>{t('rx.f.plan')}<select bind:value={sim.plan}>{#each plans as p (p)}<option value={p}>{t(`rx.o.${p}`)}</option>{/each}</select></label>
			<label>{t('rx.f.currency')}<select bind:value={sim.currency}>{#each currencies as c (c)}<option>{c}</option>{/each}</select></label>
			<label>{t('rx.f.billing_cycle')}<select bind:value={sim.cycle}><option value="monthly">{t('rx.o.monthly')}</option><option value="annual">{t('rx.o.annual')}</option></select></label>
			{#each services as s (s)}<label>{t(`rx.o.${s}`)} ({t('adm.pricing.qty')})<input type="number" min="0" bind:value={sim[s]} /></label>{/each}
			<label>{t('rx.f.discount_percent')}<input type="number" min="0" max="100" bind:value={sim.discount} /></label>
			<Switch label={t('rx.o.monitoring')} bind:checked={sim.monitoring} /><Switch label={t('adm.pricing.integrationFee')} bind:checked={sim.integrationFee} />
		</div>
		<dl class="res">
			<div><dt>{t('rx.f.subscription_amount')}</dt><dd>{money(preview.subscription)}</dd></div>
			{#each services as s (s)}<div><dt>{t(`rx.o.${s}`)}</dt><dd>{money(preview.consumption[s])}</dd></div>{/each}
			<div><dt>{t('rx.f.options_amount')}</dt><dd>{money(preview.options)}</dd></div>
			<div><dt>{t('rx.f.integration_fee')}</dt><dd>{money(preview.integrationFee)}</dd></div>
			<div><dt>{t('rx.f.discount')}</dt><dd>−{money(preview.discount)}</dd></div>
			<div><dt>{t('adm.pricing.computed')}</dt><dd>{money(preview.computed)}</dd></div>
			{#if preview.minimum}<div><dt>{t('adm.pricing.minimum')}</dt><dd>{money(preview.minimum)}</dd></div>{/if}
			<div class="tot"><dt>{t('rx.f.total')}</dt><dd>{money(preview.total)}</dd>{#if preview.minimumApplied}<small>{t('adm.pricing.minApplied')}</small>{/if}</div>
		</dl>
	</div>
</Card>

<style lang="scss">
	.ver { color: var(--fg-muted); font-size: var(--fs-sm); }
	.mx { overflow-x: auto; } table { min-width: 560px; font-size: var(--fs-sm); } th, td { padding: 0.4rem 0.5rem; text-align: left; } thead th { color: var(--fg-muted); font-size: var(--fs-xs); } tbody th { font-weight: 700; white-space: nowrap; }
	td input { width: 100%; min-width: 80px; padding: 0.5rem 0.6rem; border: 1.5px solid var(--border-strong); border-radius: var(--radius-sm); background: var(--surface); text-align: right; font-variant-numeric: tabular-nums; &:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px var(--ring); } &:disabled { opacity: 0.6; } }
	.sim { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start; } label { display: grid; gap: 0.3rem; font-size: var(--fs-sm); font-weight: 700; } select, label input { padding: 0.6rem 0.8rem; border: 1.5px solid var(--border-strong); border-radius: var(--radius-sm); background: var(--surface); font-weight: 400; }
	.res { display: grid; gap: 0.5rem; margin: 0; padding: 1.2rem; background: var(--surface-2); border-radius: var(--radius-lg); div { display: flex; justify-content: space-between; gap: 1rem; } dt { color: var(--fg-muted); font-size: var(--fs-sm); } dd { margin: 0; font-weight: 700; font-variant-numeric: tabular-nums; } .tot { border-top: 2px solid var(--border-strong); padding-top: 0.7rem; margin-top: 0.3rem; flex-wrap: wrap; dt { color: var(--fg); font-weight: 800; } dd { font-size: var(--fs-xl); } small { width: 100%; text-align: right; color: var(--warning); font-weight: 700; } } }
	@media (max-width: 900px) { .sim { grid-template-columns: 1fr; } }
</style>