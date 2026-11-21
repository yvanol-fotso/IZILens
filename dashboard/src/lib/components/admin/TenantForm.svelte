<script lang="ts">
	import { enhance } from '$app/forms';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { MODULES } from '$lib/config/modules';
	import { toastSuccess } from '$lib/stores/toast';
	import type { FormState } from '$lib/types';
	import { Button, FormAlert, Input, Modal, Switch } from '$lib/components/shared';

	let { open = $bindable(false), form }: { open?: boolean; form?: FormState | null } = $props();
	const { t } = getI18n();
	let loading = $state(false);
	let name = $state('');
	let slug = $state('');
	let touched = false;
	let checked = $state<Record<string, boolean>>({ kyc: true, api: true, liveness: false, biometrics: false, aml: false });
	$effect(() => {
		if (!touched) slug = name.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
	});
	const err = (k: string) => (form?.errors?.[k] ? t(form.errors[k]) : undefined);
</script>

<Modal bind:open title={t('admin.tenants.create')}>
	<form id="tenant" method="POST" action="?/create" class="stack" use:enhance={() => { loading = true; return async ({ result, update }) => { if (result.type === 'success') { toastSuccess(t('admin.tenants.created')); open = false; name = ''; slug = ''; touched = false; } await update({ reset: false }); loading = false; }; }}>
		<FormAlert {form} />
		<Input label={t('common.name')} name="name" bind:value={name} error={err('name')} required />
		<Input label={t('admin.tenants.slug')} name="slug" bind:value={slug} oninput={() => (touched = true)} hint={t('admin.tenants.slugHint')} error={err('slug')} required />
		<Input label="{t('admin.tenants.adminEmail')} ({t('common.optional')})" name="admin_email" type="email" error={err('admin_email')} />
		<fieldset>
			<legend>{t('admin.tenants.modules')}</legend>
			{#each MODULES as m (m.id)}
				<Switch bind:checked={checked[m.id]} label={t(`modules.${m.id}.title`)} description={t(`modules.${m.id}.desc`)} />
				{#if checked[m.id]}<input type="hidden" name="modules" value={m.id} />{/if}
			{/each}
		</fieldset>
	</form>
	{#snippet footer()}
		<Button variant="ghost" onclick={() => (open = false)}>{t('common.cancel')}</Button>
		<Button type="submit" form="tenant" variant="brand" {loading}>{t('common.create')}</Button>
	{/snippet}
</Modal>

<style lang="scss">
	fieldset { border: 0; padding: 0; margin: 0; display: grid; gap: 0.9rem; } legend { font-size: var(--fs-sm); font-weight: 700; margin-bottom: 0.6rem; }
</style>
