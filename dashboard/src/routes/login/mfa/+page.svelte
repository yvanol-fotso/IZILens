<script lang="ts">
	import { enhance } from '$app/forms';
	import { ShieldCheck } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { AuthShell } from '$lib/components/auth';
	import { Button, FormAlert, Input } from '$lib/components/shared';
	let { form } = $props();
	const { t } = getI18n();
	let loading = $state(false);
</script>

<svelte:head><title>{t('auth.mfa.title')} · IZI LENS</title></svelte:head>
<AuthShell>
	<span class="ico"><ShieldCheck size={30} /></span>
	<h1>{t('auth.mfa.title')}</h1>
	<p class="sub">{t('auth.mfa.subtitle')}</p>
	<form method="POST" class="stack" use:enhance={() => { loading = true; return async ({ update }) => { await update({ reset: true }); loading = false; }; }}>
		<FormAlert {form} />
		<Input label={t('auth.mfa.code')} name="code" inputmode="text" autocomplete="one-time-code" maxlength={24} required hint={t('auth.mfa.hint')} />
		<Button type="submit" block size="lg" {loading}>{t('auth.mfa.submit')}</Button>
	</form>
	<p class="alt"><a href="/login">{t('common.back')}</a></p>
</AuthShell>

<style lang="scss">
	.ico { width: 58px; height: 58px; border-radius: 18px; display: grid; place-items: center; background: var(--brand-navy); color: var(--brand-cyan); margin-bottom: 1rem; } h1 { font-size: var(--fs-2xl); } .sub { color: var(--fg-muted); margin: 0.4rem 0 1.6rem; } .alt { margin-top: 1.4rem; text-align: center; font-size: var(--fs-sm); }
</style>
