<script lang="ts">
	import { enhance } from '$app/forms';
	import { getI18n } from '$lib/i18n/index.svelte';
	import type { FormState, SessionUser } from '$lib/types';
	import { Button, Card, FormAlert, Input } from '$lib/components/shared';

	let { user, form }: { user: SessionUser; form?: FormState | null } = $props();
	const { t } = getI18n();
	let name = $state(user.full_name);
	let loading = $state(false);
	const mine = $derived(form?.form === 'profile' ? form : null);
</script>

<Card title={t('settings.profile.title')}>
	<form method="POST" action="?/profile" class="stack" use:enhance={() => { loading = true; return async ({ update }) => { await update({ reset: false }); loading = false; }; }}>
		<FormAlert form={mine} successMessage={t('settings.profile.saved')} />
		<Input label={t('settings.profile.fullName')} name="full_name" bind:value={name} error={mine?.errors?.full_name ? t(mine.errors.full_name) : undefined} required />
		<Input label={t('settings.profile.email')} value={user.email} disabled />
		<div><Button type="submit" variant="brand" {loading}>{t('common.save')}</Button></div>
	</form>
</Card>
