<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { AdminStats } from '$lib/components/admin';
	import { AuditTable } from '$lib/components/audit';
	import { Card, PageHeader } from '$lib/components/shared';
	let { data } = $props();
	const { t } = getI18n();
</script>

<PageHeader title={t('admin.title')} subtitle={t('admin.subtitle')} />
<div class="stack">
	<AdminStats orgs={data.orgCount} active={data.activeOrgs} members={data.memberCount} />
	<Card title={t('admin.recentActivity')} padded={false}><AuditTable logs={data.audit} /></Card>
</div>
