<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { AuthShell, LoginForm } from '$lib/components/auth';
	import { FormAlert } from '$lib/components/shared';

	let { data, form } = $props();
	const { t } = getI18n();
</script>

<svelte:head><title>{t('auth.login.title')} · IZI LENS</title></svelte:head>

<AuthShell>
	<h1>{t('auth.login.title')}</h1>
	<p class="sub">{t('auth.login.subtitle')}</p>

	{#if data.notice}<div class="notice"><FormAlert form={{ ok: true }} successMessage={t(data.notice)} /></div>{/if}
	{#if data.oauthError}<div class="notice"><FormAlert form={{ ok: false, message: data.oauthError }} /></div>{/if}

	<LoginForm {form} next={data.next} />

	<p class="alt">{t('auth.login.noAccount')} <a href="/register">{t('auth.login.signUp')}</a></p>
</AuthShell>

<style lang="scss">
	h1 { font-size: var(--fs-2xl); }
	.sub { color: var(--fg-muted); margin: 0.4rem 0 1.6rem; }
	.notice { margin-bottom: 1rem; }
	.alt { margin-top: 1.6rem; text-align: center; font-size: var(--fs-sm); color: var(--fg-muted); a { font-weight: 700; } }
</style>
