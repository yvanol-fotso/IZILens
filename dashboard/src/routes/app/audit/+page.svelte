<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { AuditTable } from '$lib/components/audit';
	import { Card, PageHeader, Pagination } from '$lib/components/shared';
	let { data } = $props();
	const { t } = getI18n();
</script>

<PageHeader title={t('audit.title')} subtitle={t('audit.subtitle')} />
<Card padded={false}>
	<AuditTable logs={data.logs.items} />
	<Pagination page={data.logs.page} pageSize={data.logs.pageSize} total={data.logs.total} />
</Card>
