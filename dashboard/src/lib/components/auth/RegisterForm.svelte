<script lang="ts">
	import { enhance } from '$app/forms';
	import { Lock, Mail, User } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import type { FormState } from '$lib/types';
	import { Button, FormAlert, Input } from '$lib/components/shared';
	import GoogleButton from './GoogleButton.svelte';

	let { form }: { form?: FormState | null } = $props();
	const { t } = getI18n();
	let loading = $state(false);
	let name = $state(form?.values?.full_name ?? '');
	let email = $state(form?.values?.email ?? '');
	const err = (k: string) => (form?.errors?.[k] ? t(form.errors[k]) : undefined);
</script>

<form method="POST" use:enhance={() => { loading = true; return async ({ update }) => { await update({ reset: false }); loading = false; }; }} class="stack" novalidate>
	<FormAlert {form} />
	<Input label={t('auth.register.fullName')} name="full_name" autocomplete="name" icon={User} bind:value={name} error={err('full_name')} required />
	<Input label={t('auth.register.email')} name="email" type="email" autocomplete="email" icon={Mail} bind:value={email} error={err('email')} required />
	<Input label={t('auth.register.password')} name="password" type="password" autocomplete="new-password" icon={Lock} hint={t('auth.register.passwordHint')} error={err('password')} required />
	<Input label={t('auth.register.confirm')} name="confirm" type="password" autocomplete="new-password" icon={Lock} error={err('confirm')} required />
	<Button type="submit" block size="lg" {loading}>{t('auth.register.submit')}</Button>
	<p class="terms">{t('auth.register.terms')}</p>
</form>

<div class="or"><span>{t('auth.login.or')}</span></div>
<GoogleButton />

<style lang="scss">
	.terms { font-size: var(--fs-xs); color: var(--fg-muted); }
	.or { display: flex; align-items: center; gap: 1rem; margin: 1.4rem 0; color: var(--fg-subtle); font-size: var(--fs-sm); &::before, &::after { content: ''; flex: 1; height: 1px; background: var(--border); } }
</style>
