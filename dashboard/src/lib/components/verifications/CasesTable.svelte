<script lang="ts">
	import { FileSearch } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { formatDate, formatPercent } from '$lib/utils/format';
	import type { KycCase } from '$lib/types';
	import { EmptyState, RiskBadge, StatusBadge, Table } from '$lib/components/shared';

	let { cases }: { cases: KycCase[] } = $props();
	const i18n = getI18n();
	const { t } = i18n;
</script>

{#if cases.length === 0}
	<EmptyState icon={FileSearch} title={t('verifications.empty.title')} description={t('verifications.empty.desc')} />
{:else}
	<Table caption={t('verifications.title')}>
		<thead>
			<tr>
				<th>{t('verifications.columns.reference')}</th><th>{t('verifications.columns.type')}</th><th>{t('verifications.columns.status')}</th>
				<th>{t('verifications.columns.risk')}</th><th class="num">{t('verifications.columns.confidence')}</th><th>{t('verifications.columns.date')}</th>
			</tr>
		</thead>
		<tbody>
			{#each cases as c (c.id)}
				<tr>
					<td><a class="cell-link" href="/app/verifications/{c.id}">{c.reference || c.id.slice(0, 8)}</a></td>
					<td>{t(`docTypes.${c.document_type}`) === `docTypes.${c.document_type}` ? c.document_type : t(`docTypes.${c.document_type}`)}</td>
					<td><StatusBadge status={c.status} /></td>
					<td><RiskBadge level={c.risk_level} /></td>
					<td class="num">{formatPercent(c.ocr_confidence, i18n.locale)}</td>
					<td>{formatDate(c.created_at, i18n.locale, true)}</td>
				</tr>
			{/each}
		</tbody>
	</Table>
{/if}
