<script lang="ts">
	import { enhance } from '$app/forms';
	import { ArrowLeft } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { MembersAdminTable, TenantModules } from '$lib/components/admin';
	import { Badge, Button, Card, PageHeader } from '$lib/components/shared';
	let { data } = $props();
	const { t } = getI18n();
</script>

<PageHeader title={data.tenant.name} subtitle={data.tenant.slug}>
	{#snippet actions()}
		<Button href="/app/admin/tenants" variant="ghost">{#snippet icon()}<ArrowLeft size={18} />{/snippet}{t('common.back')}</Button>
		<form method="POST" action="?/status" use:enhance={() => async ({ update }) => update({ reset: false })}>
			<input type="hidden" name="is_active" value={String(!data.tenant.is_active)} />
			<Button type="submit" variant={data.tenant.is_active ? 'danger' : 'brand'}>{data.tenant.is_active ? t('admin.tenants.suspend') : t('admin.tenants.reactivate')}</Button>
		</form>
	{/snippet}
</PageHeader>

<div class="grid">
	{#key data.tenant.id + data.tenant.enabled_modules.join()}<TenantModules tenant={data.tenant} />{/key}
	<Card title={t('admin.tenants.members')} padded={false}><MembersAdminTable members={data.members} /></Card>
</div>
<p class="st"><Badge tone={data.tenant.is_active ? 'success' : 'neutral'} dot>{data.tenant.is_active ? t('common.active') : t('common.inactive')}</Badge></p>

<style>
	.grid { display: grid; grid-template-columns: 360px 1fr; gap: 1.25rem; align-items: start; } .st { margin-top: 1rem; }
	@media (max-width: 960px) { .grid { grid-template-columns: 1fr; } }
</style>
