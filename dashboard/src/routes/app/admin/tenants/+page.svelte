<script lang="ts">
	import { Plus } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { TenantForm, TenantsTable } from '$lib/components/admin';
	import { Button, Card, PageHeader } from '$lib/components/shared';
	let { data, form } = $props();
	const { t } = getI18n();
	let open = $state(false);
</script>

<PageHeader title={t('admin.tenants.title')} subtitle={t('admin.tenants.subtitle')}>
	{#snippet actions()}<Button onclick={() => (open = true)}>{#snippet icon()}<Plus size={18} />{/snippet}{t('admin.tenants.create')}</Button>{/snippet}
</PageHeader>
<Card padded={false}><TenantsTable tenants={data.tenants} /></Card>
<TenantForm bind:open {form} />
