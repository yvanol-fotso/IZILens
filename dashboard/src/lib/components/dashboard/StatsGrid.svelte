<script lang="ts">
	import { CheckCircle2, ClipboardList, Gauge, ShieldAlert, Clock3, XCircle } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { formatNumber, formatPercent } from '$lib/utils/format';
	import type { CaseStats } from '$lib/server/analytics';
	import { StatCard } from '$lib/components/shared';

	let { stats }: { stats: CaseStats } = $props();
	const i18n = getI18n();
	const { t } = i18n;
</script>

<div class="grid">
	<StatCard label={t('dashboard.stats.total')} value={formatNumber(stats.total, i18n.locale)} icon={ClipboardList} />
	<StatCard label={t('dashboard.stats.pending')} value={stats.byStatus.manual_review} icon={Clock3} tone="warning" />
	<StatCard label={t('dashboard.stats.approved')} value={stats.byStatus.verified} icon={CheckCircle2} tone="success" hint="{t('dashboard.stats.approvalRate')} : {formatPercent(stats.approvalRate, i18n.locale)}" />
	<StatCard label={t('dashboard.stats.rejected')} value={stats.byStatus.not_verified} icon={XCircle} tone="danger" />
	<StatCard label={t('dashboard.stats.highRisk')} value={stats.byRisk.high} icon={ShieldAlert} tone="danger" />
	<StatCard label={t('dashboard.stats.confidence')} value={formatPercent(stats.avgConfidence, i18n.locale)} icon={Gauge} tone="info" />
</div>

<style lang="scss">
	.grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); }
</style>
