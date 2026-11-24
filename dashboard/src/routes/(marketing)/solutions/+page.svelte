<script lang="ts">
	import { demoHref } from '$lib/config/services';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { InternationalBand, ModuleComposer, SectorsGrid, TechBand, WhyModules } from '$lib/components/solutions';
	import { BulletList, Button, CtaBand, PageHero } from '$lib/components/shared';
	import { quoteHref } from '$lib/config/services';
	const { t, list } = getI18n();
</script>

<svelte:head><title>{t('nav.solutions')} · IZI LENS</title><meta name="description" content={t('sol.hero.text1')} /></svelte:head>

<PageHero kicker={t('sol.hero.kicker')} title={t('sol.hero.title')}>
	<p>{t('sol.hero.text1')}</p><p>{t('sol.hero.text2')}</p>
	{#snippet actions()}
		<Button href="#sectors" size="lg">{t('sol.hero.primary')}</Button>
		<Button href={demoHref} size="lg" variant="outline" class="ghost-light">{t('sol.hero.secondary')}</Button>
	{/snippet}
</PageHero>

<section class="intro">
	<div class="container wrap">
		<div><h2>{t('sol.intro.title')}</h2><p>{t('sol.intro.p1')}</p><p>{t('sol.intro.p2')}</p><p>{t('sol.intro.p3')}</p></div>
		<div class="mods"><p class="h">{t('sol.intro.modulesTitle')}</p><BulletList items={list('sol.intro.modules')} /></div>
	</div>
</section>

<SectorsGrid />
<ModuleComposer />
<InternationalBand />
<TechBand title={t('sol.tech.title')} text={t('sol.tech.text')} intro={t('sol.tech.intro')} items={list('sol.tech.list')} note={t('sol.tech.note')} primary={t('sol.tech.primary')} secondary={t('sol.tech.secondary')} />
<WhyModules />

<CtaBand title={t('sol.final.title')}>
	<p>{t('sol.final.text')}</p>
	{#snippet actions()}
		<Button href={demoHref} size="lg">{t('common.demo')}</Button>
		<Button href={quoteHref()} size="lg" variant="outline" class="ghost-light">{t('common.customQuote')}</Button>
	{/snippet}
</CtaBand>

<style lang="scss">
	.intro { padding: 5.5rem 0 3rem; background: var(--bg); } .wrap { display: grid; grid-template-columns: 1.3fr 1fr; gap: 3.5rem; align-items: start; }
	h2 { font-size: var(--fs-3xl); margin-bottom: 1.2rem; } .wrap p { color: var(--fg-muted); margin-bottom: 0.9rem; font-size: var(--fs-lg); }
	.mods { padding: 1.8rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); display: grid; gap: 1rem; .h { font-weight: 800; color: var(--fg); font-size: var(--fs-md); margin: 0; } :global(li) { font-size: var(--fs-sm); } }
	@media (max-width: 900px) { .wrap { grid-template-columns: 1fr; } }
</style>
