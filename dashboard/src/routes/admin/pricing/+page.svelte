<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { can } from '$lib/config/permissions';
	import { PricingEditor } from '$lib/components/billing';
	import { DataTable, UnavailableNotice } from '$lib/components/resource';
	import { Card, PageHeader } from '$lib/components/shared';
	let { data, form } = $props();
	const { t } = getI18n();
</script>

<PageHeader title={t('adm.pricing.title')} subtitle={t('adm.pricing.subtitle')} />
{#if data.unavailable}
	<Card padded={false}><UnavailableNotice endpoint="/admin/pricing" /></Card>
{:else}
	{#key data.pricing?.version}<PricingEditor pricing={data.pricing} currencies={data.currencies} {form} canWrite={can(data.user.role, 'adm:pricing:write')} />{/key}
	<div class="hist"><Card title={t('adm.pricing.history')} padded={false}>
		<DataTable cols={[{ key: 'version', type: 'mono' }, { key: 'effective_from', type: 'date' }, { key: 'created_at', type: 'datetime' }, { key: 'author' }, { key: 'reason' }]} rows={data.history} />
	</Card></div>
{/if}

<style>
	.hist { margin-top: 1.25rem; }
</style>
