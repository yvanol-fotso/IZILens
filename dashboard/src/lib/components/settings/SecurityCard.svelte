<script lang="ts">
	import { enhance } from '$app/forms';
	import { getI18n } from '$lib/i18n/index.svelte';
	import type { FormState } from '$lib/types';
	import { Button, Card, FormAlert, Input } from '$lib/components/shared';

	let { form }: { form?: FormState | null } = $props();
	const { t } = getI18n();
	let loading = $state(false);
	const mine = $derived(form?.form === 'password' ? form : null);
	const err = (k: string) => (mine?.errors?.[k] ? t(mine.errors[k]) : undefined);
</script>

<Card title={t('settings.security.title')} description={t('settings.security.googleNote')}>
	<form method="POST" action="?/password" class="stack" use:enhance={() => { loading = true; return async ({ update }) => { await update({ reset: true }); loading = false; }; }}>
		<FormAlert form={mine} successMessage={t('settings.security.changed')} />
		<Input label={t('settings.security.currentPassword')} name="current_password" type="password" autocomplete="current-password" error={err('current_password')} />
		<Input label={t('settings.security.newPassword')} name="new_password" type="password" autocomplete="new-password" hint={t('auth.register.passwordHint')} error={err('new_password')} />
		<div><Button type="submit" variant="brand" {loading}>{t('settings.security.change')}</Button></div>
	</form>
</Card>
