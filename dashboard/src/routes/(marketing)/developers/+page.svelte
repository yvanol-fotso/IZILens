<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { AccessProcess, ApiCards, EnvironmentsBand, TechSections } from '$lib/components/developers';
	import { BulletList, Button, CtaBand, PageHero } from '$lib/components/shared';
	const { t, list } = getI18n();
</script>

<svelte:head><title>{t('nav.developers')} · IZI LENS</title><meta name="description" content={t('dev.hero.text2')} /></svelte:head>

<PageHero kicker={t('dev.hero.kicker')} title={t('dev.hero.title')}>
	<p>{t('dev.hero.text1')}</p><p>{t('dev.hero.text2')}</p>
	{#snippet actions()}
		<Button href="/contact?type=developer#form" size="lg">{t('dev.hero.primary')}</Button>
		<Button href="/login" size="lg" variant="outline" class="ghost-light">{t('dev.hero.secondary')}</Button>
	{/snippet}
</PageHero>

<section class="intro">
	<div class="container wrap">
		<div><h2>{t('dev.intro.title')}</h2><p>{t('dev.intro.text')}</p></div>
		<div class="box"><p class="h">{t('dev.intro.intro')}</p><BulletList items={list('dev.intro.list')} /></div>
	</div>
</section>

<ApiCards />
<TechSections />
<AccessProcess />
<EnvironmentsBand />

<CtaBand title={t('dev.support.title')}>
	<p>{t('dev.support.text')}</p>
	{#snippet actions()}
		<Button href="/contact?type=developer#form" size="lg">{t('dev.support.primary')}</Button>
		<Button href="/contact?type=integration#form" size="lg" variant="outline" class="ghost-light">{t('dev.support.secondary')}</Button>
	{/snippet}
</CtaBand>

<style lang="scss">
	.intro { padding: 5.5rem 0 3rem; background: var(--bg); } .wrap { display: grid; grid-template-columns: 1.2fr 1fr; gap: 3.5rem; align-items: start; }
	h2 { font-size: var(--fs-3xl); margin-bottom: 1rem; } .wrap p { color: var(--fg-muted); font-size: var(--fs-lg); }
	.box { padding: 1.8rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); display: grid; gap: 1rem; .h { font-weight: 800; color: var(--fg); font-size: var(--fs-md); } :global(li) { font-size: var(--fs-sm); } }
	@media (max-width: 900px) { .wrap { grid-template-columns: 1fr; } }
</style>
