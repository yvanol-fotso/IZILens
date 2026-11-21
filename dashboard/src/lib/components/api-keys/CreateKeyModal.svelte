<script lang="ts">
	import { enhance } from '$app/forms';
	import { getI18n } from '$lib/i18n/index.svelte';
	import type { FormState } from '$lib/types';
	import { Button, FormAlert, Input, Modal, Select } from '$lib/components/shared';

	let { open = $bindable(false), form, onCreated }: { open?: boolean; form?: FormState | null; onCreated: (c: { name: string; key: string }) => void } = $props();
	const { t } = getI18n();
	let name = $state('');
	let days = $state('90');
	let loading = $state(false);
</script>

<Modal bind:open title={t('apiKeys.create')}>
	<form id="create-key" method="POST" action="?/create" class="stack" use:enhance={() => { loading = true; return async ({ result, update }) => { if (result.type === 'success' && result.data?.created) { onCreated(result.data.created as { name: string; key: string }); name = ''; open = false; } await update({ reset: false, invalidateAll: true }); loading = false; }; }}>
		<FormAlert {form} />
		<Input label={t('apiKeys.name')} name="name" bind:value={name} placeholder={t('apiKeys.namePlaceholder')} maxlength={80} required />
		<Select label={t('apiKeys.expiry')} name="expires_in_days" bind:value={days} options={[{ value: '30', label: t('apiKeys.expiry30') }, { value: '90', label: t('apiKeys.expiry90') }, { value: '365', label: t('apiKeys.expiry365') }, { value: '0', label: t('apiKeys.expiryNever') }]} />
	</form>
	{#snippet footer()}
		<Button variant="ghost" onclick={() => (open = false)}>{t('common.cancel')}</Button>
		<Button type="submit" form="create-key" variant="brand" {loading}>{t('common.create')}</Button>
	{/snippet}
</Modal>
