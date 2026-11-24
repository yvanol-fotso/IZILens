<script lang="ts">
	import { demoHref, quoteHref } from '$lib/config/services';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { ServiceComposer, ServicesOverview } from '$lib/components/services';
	import { SectorsGrid, TechBand } from '$lib/components/solutions';
	import { BulletList, Button, CtaBand, PageHero, SectionHeader } from '$lib/components/shared';
	const { t, list } = getI18n();
</script>

<svelte:head><title>{t('svc.hero.title')} · IZI LENS</title><meta name="description" content={t('svc.hero.text1')} /></svelte:head>

<PageHero kicker={t('svc.hero.kicker')} title={t('svc.hero.title')}>
	<p>{t('svc.hero.text1')}</p><p>{t('svc.hero.text2')}</p>
	{#snippet actions()}
		<Button href="#solutions" size="lg">{t('svc.hero.primary')}</Button>
		<Button href={quoteHref()} size="lg" variant="outline" class="ghost-light">{t('svc.hero.secondary')}</Button>
	{/snippet}
</PageHero>

<ServicesOverview />
<ServiceComposer />
<SectorsGrid compact title={t('svc.sectors.title')} text={t('svc.sectors.text')} note={t('svc.sectors.note')} />
<TechBand title={t('svc.integration.title')} text={t('svc.integration.text')} intro={t('svc.integration.intro')} items={list('svc.integration.list')} primary={t('svc.integration.primary')} secondary={t('svc.integration.secondary')} />

<section class="price">
	<div class="container wrap">
		<SectionHeader title={t('svc.pricing.title')}><p>{t('svc.pricing.text')}</p></SectionHeader>
		<div class="box"><p class="intro">{t('svc.pricing.intro')}</p><BulletList items={list('svc.pricing.list')} /><Button href={quoteHref()} variant="brand">{t('common.customQuote')}</Button></div>
	</div>
</section>

<CtaBand title={t('svc.final.title')}>
	<p>{t('svc.final.text')}</p>
	{#snippet actions()}
		<Button href={demoHref} size="lg">{t('common.demo')}</Button>
		<Button href={quoteHref()} size="lg" variant="outline" class="ghost-light">{t('common.quote')}</Button>
	{/snippet}
</CtaBand>

<style lang="scss">
	.price { padding: 5.5rem 0; background: var(--bg-soft); border-top: 1px solid var(--border); }
	.wrap { display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; align-items: center; } .intro { font-weight: 800; }
	.box { display: grid; gap: 1.2rem; padding: 2rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-xl); justify-items: start; }
	@media (max-width: 900px) { .wrap { grid-template-columns: 1fr; } }
</style>
