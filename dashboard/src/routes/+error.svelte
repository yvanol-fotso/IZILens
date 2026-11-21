<script lang="ts">
	import { page } from '$app/state';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Button, Logo } from '$lib/components/shared';

	const { t } = getI18n();
	const status = $derived(page.status);
	const code = $derived((page.error as { code?: string } | null)?.code);
	const message = $derived.by(() => {
		if (code === 'backend_unreachable' || page.error?.message === 'backend_unreachable') return t('errors.backend_unreachable');
		if (status === 403) return t('errors.forbidden');
		if (status === 404) return t('errors.notFound');
		return page.error?.message && page.error.message !== 'Internal Error' ? page.error.message : t('errors.generic');
	});
	const inApp = $derived(page.url.pathname.startsWith('/app'));
</script>

<svelte:head><title>{status} · IZI LENS</title></svelte:head>

<main id="main" class="err">
	<Logo size={44} />
	<p class="code">{status}</p>
	<h1>{message}</h1>
	<Button href={inApp ? '/app' : '/'} variant="brand">{inApp ? t('errors.goDashboard') : t('errors.goHome')}</Button>
</main>

<style lang="scss">
	.err { min-height: 100dvh; display: grid; place-content: center; justify-items: center; gap: 1.2rem; text-align: center; padding: 2rem; }
	.code { font-size: clamp(5rem, 18vw, 9rem); font-weight: 800; letter-spacing: -0.06em; line-height: 0.9; background: linear-gradient(135deg, var(--brand-cyan), var(--brand-blue)); -webkit-background-clip: text; background-clip: text; color: transparent; }
	h1 { font-size: var(--fs-xl); max-width: 32ch; }
</style>
