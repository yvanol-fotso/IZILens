<script lang="ts">
	import { CalendarClock, Receipt } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { clientResource } from '$lib/config/client-resources';
	import { formatDate, formatNumber } from '$lib/utils/format';
	import { DataTable, UnavailableNotice } from '$lib/components/resource';
	import { Badge, Button, Card, PageHeader } from '$lib/components/shared';
	let { data } = $props();
	const i18n = getI18n();
	const { t } = i18n;
	const s = $derived(data.summary ?? {});
	const cur = $derived(s.currency ?? 'CAD');
	const money = (v: any) => (typeof v === 'number' ? new Intl.NumberFormat(i18n.locale === 'fr' ? 'fr-CA' : 'en-CA', { style: 'currency', currency: cur, maximumFractionDigits: ['XOF', 'XAF'].includes(cur) ? 0 : 2 }).format(v) : '—');
	const services = ['kyc', 'kyb', 'biometrics'];
	const tabs = ['invoices', 'payments', 'usage'];
</script>

<PageHeader title={t('cli.billing.title')} subtitle={t('cli.billing.subtitle')} />
{#if data.unavailable}
	<Card padded={false}><UnavailableNotice endpoint="/billing/summary" /></Card>
{:else}
	<div class="top">
		<Card><div class="plan"><span class="lbl">{t('cli.billing.plan')}</span><Badge tone="brand">{t(`rx.o.${s.plan ?? 'starter'}`)}</Badge><span class="muted">{t(`rx.o.${s.billing_cycle ?? 'monthly'}`)}</span></div>
			<strong class="sub">{money(s.subscription_amount)}</strong><small>{t('rx.f.subscription_amount')}</small></Card>
		<Card><span class="lbl"><CalendarClock size={15} /> {t('cli.billing.period')}</span><strong class="sub">{s.period ?? '—'}</strong><small>{t('cli.billing.next')} : {formatDate(s.next_invoice_at, i18n.locale)}</small></Card>
		<Card class="due"><span class="lbl"><Receipt size={15} /> {t('cli.billing.totalDue')}</span><strong class="big">{money(s.total_due)}</strong>{#if s.minimum_applied}<small class="warn">{t('adm.pricing.minApplied')}</small>{/if}</Card>
	</div>

	<Card title={t('cli.billing.consumption')} padded={false}>
		<table>
			<thead><tr><th>{t('rx.f.service')}</th><th class="n">{t('adm.pricing.qty')}</th><th class="n">{t('rx.f.amount')}</th></tr></thead>
			<tbody>
				{#each services as k (k)}<tr><td>{t(`rx.o.${k}`)}</td><td class="n">{formatNumber(s.usage?.[k]?.count, i18n.locale)}</td><td class="n">{money(s.usage?.[k]?.amount)}</td></tr>{/each}
				<tr><td>{t('rx.o.monitoring')}</td><td class="n">—</td><td class="n">{money(s.monitoring_amount)}</td></tr>
				{#if s.integration_fee}<tr><td>{t('rx.f.integration_fee')}</td><td class="n">—</td><td class="n">{money(s.integration_fee)}</td></tr>{/if}
				{#if s.discount}<tr><td>{t('rx.f.discount')}</td><td class="n">—</td><td class="n">−{money(s.discount)}</td></tr>{/if}
			</tbody>
		</table>
	</Card>

	<nav class="tabs" aria-label="Billing">{#each tabs as k (k)}<Button href="/app/{k}" variant="outline" size="sm">{t(`rx.r.${k}.title`)}</Button>{/each}</nav>
	<Card title={t('rx.r.invoices.title')} padded={false}>
		<DataTable cols={clientResource('invoices')!.cols} rows={data.invoices.items} href={(r) => `/app/invoices/${r.id}`} />
	</Card>
{/if}

<style lang="scss">
	.top { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin-bottom: 1.25rem; } .lbl { display: inline-flex; align-items: center; gap: 0.4rem; font-size: var(--fs-sm); font-weight: 700; color: var(--fg-muted); } .plan { display: flex; gap: 0.6rem; align-items: center; }
	.sub { display: block; font-size: var(--fs-2xl); margin-top: 0.4rem; } .big { display: block; font-size: 2.4rem; letter-spacing: -0.03em; margin-top: 0.3rem; } small { color: var(--fg-muted); font-size: var(--fs-xs); display: block; } .warn { color: var(--warning); font-weight: 700; }
	table { width: 100%; font-size: var(--fs-sm); } th, td { padding: 0.8rem 1.2rem; border-bottom: 1px solid var(--border); text-align: left; } th { background: var(--surface-2); font-size: var(--fs-xs); color: var(--fg-muted); } .n { text-align: right; font-variant-numeric: tabular-nums; }
	.tabs { display: flex; gap: 0.5rem; margin: 1.5rem 0 1rem; flex-wrap: wrap; }
</style>
