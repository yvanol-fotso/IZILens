<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { MembersAdminTable } from '$lib/components/admin';
	import { Card, PageHeader } from '$lib/components/shared';
	let { data } = $props();
	const { t } = getI18n();
</script>

<PageHeader title={t('admin.members.title')} subtitle={t('admin.members.subtitle')} />
<Card padded={false}><MembersAdminTable members={data.members} orgNames={data.orgNames} /></Card>
