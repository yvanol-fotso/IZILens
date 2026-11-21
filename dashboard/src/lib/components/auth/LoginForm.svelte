<script lang="ts">
	import { enhance } from '$app/forms';
	import { Lock, Mail } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import type { FormState } from '$lib/types';
	import { Button, FormAlert, Input } from '$lib/components/shared';
	import GoogleButton from './GoogleButton.svelte';

	let { form, next = '', email = '' }: { form?: FormState | null; next?: string; email?: string } = $props();
	const { t } = getI18n();
	let loading = $state(false);
	let emailValue = $state(form?.values?.email ?? email);
</script>

<form method="POST" use:enhance={() => { loading = true; return async ({ update }) => { await update({ reset: false }); loading = false; }; }} class="stack" novalidate>
	<input type="hidden" name="next" value={next} />
	<FormAlert {form} />
	<Input label={t('auth.login.email')} name="email" type="email" autocomplete="email" icon={Mail} bind:value={emailValue} error={form?.errors?.email ? t(form.errors.email) : undefined} required />
	<Input label={t('auth.login.password')} name="password" type="password" autocomplete="current-password" icon={Lock} error={form?.errors?.password ? t(form.errors.password) : undefined} required />
	<Button type="submit" block size="lg" {loading}>{t('auth.login.submit')}</Button>
</form>

<div class="or"><span>{t('auth.login.or')}</span></div>
<GoogleButton {next} />

<style lang="scss">
	.or { display: flex; align-items: center; gap: 1rem; margin: 1.4rem 0; color: var(--fg-subtle); font-size: var(--fs-sm); &::before, &::after { content: ''; flex: 1; height: 1px; background: var(--border); } }
</style>
