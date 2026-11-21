<script lang="ts">
	import { Plus } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { CreateKeyModal, KeyRevealModal, KeysTable } from '$lib/components/api-keys';
	import { Button, Card, PageHeader } from '$lib/components/shared';

	let { data, form } = $props();
	const { t } = getI18n();
	let createOpen = $state(false);
	let created = $state<{ name: string; key: string } | null>(null);
</script>

<PageHeader title={t('apiKeys.title')} subtitle={t('apiKeys.subtitle')}>
	{#snippet actions()}<Button onclick={() => (createOpen = true)}>{#snippet icon()}<Plus size={18} />{/snippet}{t('apiKeys.create')}</Button>{/snippet}
</PageHeader>

<Card padded={false}><KeysTable keys={data.keys} /></Card>
<CreateKeyModal bind:open={createOpen} {form} onCreated={(c) => (created = c)} />
<KeyRevealModal bind:created />
