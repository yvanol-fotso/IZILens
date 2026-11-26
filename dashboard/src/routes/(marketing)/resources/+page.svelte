<script lang="ts">
	import { demoHref } from '$lib/config/services';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { ResourceCenter } from '$lib/components/resources';
	import { Button, CtaBand, PageHero } from '$lib/components/shared';
	import Img from '$lib/components/shared/Img.svelte';
	const { t } = getI18n();
</script>

<svelte:head><title>{t('nav.resources')} · IZI LENS</title><meta name="description" content={t('res.hero.subtitle')} /></svelte:head>

<PageHero title={t('res.hero.title')}>
	<p>{t('res.hero.subtitle')}</p>
	{#snippet media()}
		<Img src="/marketing/resources/hero" alt={t('res.images.hero')} ratio="8/7" loading="eager" />
	{/snippet}
</PageHero>
<ResourceCenter />

<section class="dev">
	<div class="container">
		<div class="box">
			<div class="thumb"><Img src="/marketing/resources/developers" alt={t('res.images.developers')} ratio="4/3" /></div>
			<div class="txt"><h2>{t('res.dev.title')}</h2><p>{t('res.dev.text')}</p></div>
			<Button href="/developers" variant="brand">{t('res.dev.primary')}</Button>
		</div>
	</div>
</section>

<CtaBand title={t('res.cta.title')}>
	{#snippet actions()}
		<Button href={demoHref} size="lg">{t('res.cta.primary')}</Button>
		<Button href="/contact#form" size="lg" variant="outline" class="ghost-light">{t('res.cta.secondary')}</Button>
	{/snippet}
</CtaBand>

<style lang="scss">
	.dev { padding: 0 0 5rem; background: var(--bg); }
	.box { display: flex; align-items: center; gap: 2rem; flex-wrap: wrap; padding: 1.6rem 2.2rem 1.6rem 1.6rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-xl); }
	.thumb { width: 200px; flex-shrink: 0; --img-radius: var(--radius-lg); border-radius: var(--radius-lg); }
	.txt { flex: 1; min-width: 240px; h2 { font-size: var(--fs-xl); } p { color: var(--fg-muted); margin-top: 0.3rem; max-width: 56ch; } }
	@media (max-width: 640px) { .thumb { width: 100%; } .box { padding: 1.2rem; } }
</style>
