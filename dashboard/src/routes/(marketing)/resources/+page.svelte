<script lang="ts">
	import { demoHref } from '$lib/config/services';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { ResourceCenter } from '$lib/components/resources';
	import { Button, CtaBand, PageHero } from '$lib/components/shared';
	const { t } = getI18n();
</script>

<svelte:head><title>{t('nav.resources')} · IZI LENS</title><meta name="description" content={t('res.hero.subtitle')} /></svelte:head>

<PageHero title={t('res.hero.title')}><p>{t('res.hero.subtitle')}</p></PageHero>
<ResourceCenter />

<section class="dev"><div class="container"><div class="box"><div><h2>{t('res.dev.title')}</h2><p>{t('res.dev.text')}</p></div><Button href="/developers" variant="brand">{t('res.dev.primary')}</Button></div></div></section>

<CtaBand title={t('res.cta.title')}>
	{#snippet actions()}
		<Button href={demoHref} size="lg">{t('res.cta.primary')}</Button>
		<Button href="/contact#form" size="lg" variant="outline" class="ghost-light">{t('res.cta.secondary')}</Button>
	{/snippet}
</CtaBand>

<style lang="scss">
	.dev { padding: 0 0 5rem; background: var(--bg); } .box { display: flex; justify-content: space-between; align-items: center; gap: 2rem; flex-wrap: wrap; padding: 2rem 2.2rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-xl); h2 { font-size: var(--fs-xl); } p { color: var(--fg-muted); margin-top: 0.3rem; max-width: 56ch; } }
</style>
