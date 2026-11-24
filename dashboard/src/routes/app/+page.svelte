<script lang="ts">
	import { FilePlus2 } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { can } from '$lib/config/permissions';
	import { ModulesCard, RecentCases, StatsGrid } from '$lib/components/dashboard';
	import { BarChart, Button, Card, DonutChart, PageHeader } from '$lib/components/shared';

	let { data } = $props();
	const { t } = getI18n();
	const user = $derived(data.user);
	const s = $derived(data.stats);
	const statusSegments = $derived([
		{ label: t('status.verified'), value: s.byStatus.verified, color: 'var(--accent-mint)' },
		{ label: t('status.manual_review'), value: s.byStatus.manual_review, color: 'var(--accent-orange)' },
		{ label: t('status.not_verified'), value: s.byStatus.not_verified, color: 'var(--accent-rose)' },
		{ label: t('status.processing'), value: s.byStatus.processing + s.byStatus.in_progress, color: 'var(--brand-blue)' },
		{ label: t('status.action_required'), value: s.byStatus.action_required, color: 'var(--accent-violet, var(--brand-blue))' },
		{ label: t('status.failed'), value: s.byStatus.failed + s.byStatus.expired, color: 'var(--fg-subtle)' }
	]);
</script>

<PageHeader title={t('dashboard.welcome', { name: user.full_name.split(' ')[0] })} subtitle={t('dashboard.subtitle')}>
	{#snippet actions()}
		{#if can(user.role, 'cases:create')}
			<Button href="/app/verifications/new">{#snippet icon()}<FilePlus2 size={18} />{/snippet}{t('verifications.new')}</Button>
		{/if}
	{/snippet}
</PageHeader>

<div class="page">
	<StatsGrid stats={s} />
	<div class="two">
		<Card title={t('dashboard.volume')}><BarChart data={s.daily} /></Card>
		<Card title={t('dashboard.byStatus')}><DonutChart segments={statusSegments} centerLabel={t('dashboard.stats.total')} /></Card>
	</div>
	<div class="two wide-left">
		<RecentCases cases={data.recent} />
		<ModulesCard {user} />
	</div>
</div>

<style lang="scss">
	.page { display: grid; gap: 1.25rem; }
	.two { display: grid; grid-template-columns: 1.5fr 1fr; gap: 1.25rem; &.wide-left { grid-template-columns: 1.6fr 1fr; } }
	@media (max-width: 960px) { .two, .two.wide-left { grid-template-columns: 1fr; } }
</style>
