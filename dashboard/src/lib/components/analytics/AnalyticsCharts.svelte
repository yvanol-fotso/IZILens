<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import type { CaseStats } from '$lib/server/analytics';
	import { BarChart, Card, DonutChart } from '$lib/components/shared';

	let { stats }: { stats: CaseStats } = $props();
	const { t } = getI18n();
	const bands = $derived([
		{ label: t('analytics.bands.low'), value: stats.confidenceBands.low },
		{ label: t('analytics.bands.mid'), value: stats.confidenceBands.mid },
		{ label: t('analytics.bands.high'), value: stats.confidenceBands.high }
	]);
	const risk = $derived([
		{ label: t('risk.low'), value: stats.byRisk.low, color: 'var(--accent-mint)' },
		{ label: t('risk.medium'), value: stats.byRisk.medium, color: 'var(--accent-orange)' },
		{ label: t('risk.high'), value: stats.byRisk.high, color: 'var(--accent-rose)' },
		{ label: t('risk.none'), value: stats.byRisk.none, color: 'var(--fg-subtle)' }
	]);
</script>

<div class="grid">
	<Card title={t('analytics.daily')} class="full"><BarChart data={stats.daily} height={220} /></Card>
	<Card title={t('analytics.confidence')}><BarChart data={bands} labelMode="label" height={180} /></Card>
	<Card title={t('dashboard.byRisk')}><DonutChart segments={risk} centerLabel={t('dashboard.stats.total')} /></Card>
</div>

<style lang="scss">
	.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; :global(.full) { grid-column: 1 / -1; } }
	@media (max-width: 860px) { .grid { grid-template-columns: 1fr; } }
</style>
