<script lang="ts">
	import { FilePlus2 } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { can } from '$lib/config/permissions';
	import { CaseFilters, CasesTable } from '$lib/components/verifications';
	import { Button, Card, PageHeader, Pagination } from '$lib/components/shared';

	let { data } = $props();
	const { t } = getI18n();
</script>

<PageHeader title={t('verifications.title')} subtitle={t('verifications.subtitle')}>
	{#snippet actions()}
		{#if can(data.user.role, 'cases:create')}<Button href="/app/verifications/new">{#snippet icon()}<FilePlus2 size={18} />{/snippet}{t('verifications.new')}</Button>{/if}
	{/snippet}
</PageHeader>

<Card padded={false}>
	<CaseFilters filters={data.filters} />
	<CasesTable cases={data.cases.items} />
	<Pagination page={data.cases.page} pageSize={data.cases.pageSize} total={data.cases.total} />
</Card>
