<script lang="ts">
	import { FileCheck2 } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { formatDate } from '$lib/utils/format';
	import type { KycCase } from '$lib/types';
	import { Button, Card, EmptyState, RiskBadge, StatusBadge, Table } from '$lib/components/shared';
	import { can } from '$lib/config/permissions';
	import { page } from '$app/state';

	let { cases }: { cases: KycCase[] } = $props();
	const i18n = getI18n();
	const { t } = i18n;
	const canCreate = $derived(can(page.data.user?.role, 'cases:create'));
</script>

<Card title={t('dashboard.recent')} padded={false}>
	{#snippet actions()}<Button href="/app/verifications" variant="ghost" size="sm">{t('dashboard.viewAll')}</Button>{/snippet}
	{#if cases.length === 0}
		<EmptyState icon={FileCheck2} title={t('dashboard.empty.title')} description={t('dashboard.empty.desc')}>
			{#if canCreate}<Button href="/app/verifications/new" variant="brand">{t('verifications.new')}</Button>{/if}
		</EmptyState>
	{:else}
		<Table caption={t('dashboard.recent')}>
			<thead><tr><th>{t('verifications.columns.reference')}</th><th>{t('verifications.columns.status')}</th><th>{t('verifications.columns.risk')}</th><th>{t('verifications.columns.date')}</th></tr></thead>
			<tbody>
				{#each cases as c (c.id)}
					<tr>
						<td><a class="cell-link" href="/app/verifications/{c.id}">{c.reference || c.id.slice(0, 8)}</a></td>
						<td><StatusBadge status={c.status} /></td>
						<td><RiskBadge level={c.risk_level} /></td>
						<td>{formatDate(c.created_at, i18n.locale, true)}</td>
					</tr>
				{/each}
			</tbody>
		</Table>
	{/if}
</Card>
