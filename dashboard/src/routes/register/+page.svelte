<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { AuthShell, RegisterForm } from '$lib/components/auth';

	let { form } = $props();
	const { t } = getI18n();
</script>

<svelte:head><title>{t('auth.register.title')} · IZI LENS</title></svelte:head>

<AuthShell>
	<h1>{t('auth.register.title')}</h1>
	<p class="sub">{t('auth.register.subtitle')}</p>
	<RegisterForm {form} />
	<p class="alt">{t('auth.register.haveAccount')} <a href="/login">{t('auth.register.signIn')}</a></p>
</AuthShell>

<style lang="scss">
	h1 { font-size: var(--fs-2xl); }
	.sub { color: var(--fg-muted); margin: 0.4rem 0 1.6rem; }
	.alt { margin-top: 1.6rem; text-align: center; font-size: var(--fs-sm); color: var(--fg-muted); a { font-weight: 700; } }
</style>
