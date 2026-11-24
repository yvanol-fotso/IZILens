<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { DashboardFilters, KpiSection } from '$lib/components/admin';
	import { DataTable, UnavailableNotice, toneFor } from '$lib/components/resource';
	import { Badge, BarChart, Card, PageHeader } from '$lib/components/shared';
	let { data } = $props();
	const { t } = getI18n();
	const d = $derived(data.dash ?? {});
	const cur = $derived(d.financial?.currency ?? 'CAD');
	const series = $derived((d.series?.daily ?? []).map((x: any) => ({ date: x.date, value: (x.kyc ?? 0) + (x.kyb ?? 0) + (x.biometrics ?? 0) })));
</script>

<PageHeader title={t('adm.dash.title')} subtitle={t('adm.dash.subtitle')} />
<DashboardFilters query={data.query} />

{#if data.unavailable}
	<Card padded={false}><UnavailableNotice endpoint="/admin/dashboard" /></Card>
{:else}
	<KpiSection title={t('adm.dash.clients')} data={d.clients} />
	<KpiSection title={t('adm.dash.kyc')} data={d.kyc} />
	<KpiSection title={t('adm.dash.kyb')} data={d.kyb} />
	<KpiSection title={t('adm.dash.biometrics')} data={d.biometrics} />
	<KpiSection title={t('adm.dash.financial')} data={d.financial ? Object.fromEntries(Object.entries(d.financial).filter(([k]) => k !== 'currency')) : undefined} money currency={cur} />
	{#if series.length}<Card title={t('adm.dash.volume')}><BarChart data={series} height={200} /></Card>{/if}

	<section class="tech">
		<h2>{t('adm.dash.technical')}</h2>
		<KpiSection title="" data={d.technical ? Object.fromEntries(Object.entries(d.technical).filter(([, v]) => typeof v !== 'object')) : undefined} />
		{#if (d.technical?.providers ?? []).length}
			<Card title={t('adm.prov.status')} padded={false}><DataTable cols={[{ key: 'name' }, { key: 'status', type: 'status' }, { key: 'latency_ms', type: 'number' }]} rows={d.technical.providers} /></Card>
		{/if}
		{#if (d.technical?.alerts ?? []).length}<Card title={t('adm.dash.alerts')}><ul>{#each d.technical.alerts as a (a.message)}<li><Badge tone={toneFor(a.level)}>{a.level}</Badge> {a.message}</li>{/each}</ul></Card>{/if}
	</section>
{/if}

<style lang="scss">
	.tech { margin-top: 2rem; display: grid; gap: 1rem; } h2 { font-size: var(--fs-xl); } ul { display: grid; gap: 0.5rem; }
</style>
