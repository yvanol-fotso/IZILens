<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { formatDate } from '$lib/utils/format';
	import { DataTable, UnavailableNotice, toneFor } from '$lib/components/resource';
	import { Badge, Card, PageHeader } from '$lib/components/shared';
	let { data } = $props();
	const i18n = getI18n();
	const { t } = i18n;
	const i = $derived(data.infra ?? {});
	const gauges = $derived([
		{ k: 'cpu', v: i.cpu_percent }, { k: 'memory', v: i.memory_percent },
		{ k: 'storage', v: i.storage?.total_gb ? Math.round((i.storage.used_gb / i.storage.total_gb) * 100) : undefined }
	]);
</script>

<PageHeader title={t('adm.infra.title')} subtitle={t('adm.infra.subtitle')} />
{#if data.unavailable}
	<Card padded={false}><UnavailableNotice endpoint="/admin/infrastructure" /></Card>
{:else}
	<div class="stack">
		<Card><div class="top"><Badge tone={toneFor(i.overall_status === 'operational' ? 'active' : i.overall_status === 'degraded' ? 'pending' : 'failed')} dot>{t(`rx.o.${i.overall_status ?? 'unknown'}`)}</Badge>
			<span class="muted">{t('adm.infra.network')} : ↓ {i.network?.in_mbps ?? '—'} Mbps · ↑ {i.network?.out_mbps ?? '—'} Mbps</span></div></Card>
		<div class="g">
			{#each gauges as g (g.k)}
				<Card title={t(`adm.infra.${g.k}`)}>
					<div class="bar" role="meter" aria-valuenow={g.v ?? 0} aria-valuemin="0" aria-valuemax="100"><i style:width="{g.v ?? 0}%" class:warn={(g.v ?? 0) > 75} class:bad={(g.v ?? 0) > 90}></i></div>
					<strong>{g.v !== undefined ? `${g.v}%` : '—'}</strong>
					{#if g.k === 'storage' && i.storage}<small>{i.storage.used_gb} / {i.storage.total_gb} GB</small>{/if}
				</Card>
			{/each}
		</div>
		<Card title={t('adm.infra.services')} padded={false}><DataTable cols={[{ key: 'name' }, { key: 'status', type: 'status' }, { key: 'latency_ms', type: 'number' }, { key: 'uptime_percent', type: 'percent' }]} rows={i.services ?? []} /></Card>
		<div class="two">
			<Card title={t('adm.infra.databases')} padded={false}><DataTable cols={[{ key: 'name' }, { key: 'status', type: 'status' }, { key: 'connections', type: 'number' }]} rows={i.databases ?? []} /></Card>
			<Card title={t('adm.infra.backups')} padded={false}><DataTable cols={[{ key: 'name' }, { key: 'last_success_at', type: 'datetime' }, { key: 'status', type: 'status' }]} rows={i.backups ?? []} /></Card>
		</div>
		<Card title={t('adm.infra.incidents')} padded={false}><DataTable cols={[{ key: 'title' }, { key: 'status', type: 'status' }, { key: 'started_at', type: 'datetime' }]} rows={i.incidents ?? []} /></Card>
		{#if (i.capacity_alerts ?? []).length}<Card title={t('adm.infra.capacity')}><ul>{#each i.capacity_alerts as a (a.message)}<li><Badge tone={toneFor(a.level)}>{a.level}</Badge> {a.message}</li>{/each}</ul></Card>{/if}
		<p class="muted note">{t('adm.infra.secure')}{#if i.generated_at} · {formatDate(i.generated_at, i18n.locale, true)}{/if}</p>
	</div>
{/if}

<style lang="scss">
	.top { display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap; align-items: center; } .g { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; } .two { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
	.bar { height: 10px; border-radius: 6px; background: var(--surface-3); overflow: hidden; margin-bottom: 0.7rem; i { display: block; height: 100%; background: var(--accent-mint); &.warn { background: var(--accent-orange); } &.bad { background: var(--accent-rose); } } } strong { font-size: var(--fs-2xl); } small { display: block; color: var(--fg-muted); }
	ul { display: grid; gap: 0.5rem; } .note { font-size: var(--fs-xs); } @media (max-width: 900px) { .two { grid-template-columns: 1fr; } }
</style>
