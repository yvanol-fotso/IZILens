<script lang="ts">
	import { enhance } from '$app/forms';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { ASSIGNABLE_ROLES } from '$lib/config/permissions';
	import { toastSuccess } from '$lib/stores/toast';
	import type { FormState } from '$lib/types';
	import { Button, FormAlert, Input, Modal, Select } from '$lib/components/shared';

	let { open = $bindable(false), form }: { open?: boolean; form?: FormState | null } = $props();
	const { t } = getI18n();
	let loading = $state(false);
	let role = $state('reviewer');
	const err = (k: string) => (form?.errors?.[k] ? t(form.errors[k]) : undefined);
</script>

<Modal bind:open title={t('team.invite')}>
	<form id="invite" method="POST" action="?/invite" class="stack" use:enhance={() => { loading = true; return async ({ result, update }) => { if (result.type === 'success') { toastSuccess(t('team.added')); open = false; } await update({ reset: result.type === 'success' }); loading = false; }; }}>
		<FormAlert {form} />
		<Input label={t('team.fullName')} name="full_name" error={err('full_name')} required />
		<Input label={t('common.email')} name="email" type="email" error={err('email')} required />
		<Select label={t('common.role')} name="role" bind:value={role} hint={t(`team.roleHelp.${role}`)} options={ASSIGNABLE_ROLES.map((r) => ({ value: r, label: t(`roles.${r}`) }))} />
		<Input label={t('team.tempPassword')} name="password" type="password" autocomplete="new-password" hint={t('team.tempPasswordHint')} error={err('password')} required />
	</form>
	{#snippet footer()}
		<Button variant="ghost" onclick={() => (open = false)}>{t('common.cancel')}</Button>
		<Button type="submit" form="invite" variant="brand" {loading}>{t('common.create')}</Button>
	{/snippet}
</Modal>
