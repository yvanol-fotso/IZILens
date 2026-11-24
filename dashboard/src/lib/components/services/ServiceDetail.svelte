<script lang="ts">
	import { ArrowLeft } from '@lucide/svelte';
	import { demoHref, quoteHref, type ServiceDef } from '$lib/config/services';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { translate } from '$lib/i18n/translate';
	import { BulletList, Button, CtaBand, PageHero } from '$lib/components/shared';

	let { service }: { service: ServiceDef } = $props();
	const i18n = getI18n();
	const { t, list } = i18n;
	const faqRaw = (k: string, i: number, f: 'q' | 'a') => translate(i18n.locale, `${k}.faq.${i}.${f}`);
	const k = $derived(`svc.items.${service.id}`);
	const faqItem = (i: number) => ({ q: faqRaw(k, i, 'q'), a: faqRaw(k, i, 'a') });
</script>

<svelte:head><title>{t(`${k}.code`)} · IZI LENS</title><meta name="description" content={t(`${k}.tagline`)} /></svelte:head>

<PageHero kicker={`${t(`${k}.code`)} — ${t(`${k}.name`)}`} title={t(`${k}.tagline`)}>
	<p>{t(`${k}.intro`)}</p>
	{#snippet actions()}
		<Button href={quoteHref([service.id])} size="lg">{t('common.quote')}</Button>
		<Button href={demoHref} size="lg" variant="outline" class="ghost-light">{t('common.demo')}</Button>
	{/snippet}
</PageHero>

<div class="container body">
	<a class="back" href="/services"><ArrowLeft size={16} />{t('svc.detail.back')}</a>

	<section><h2>{t('svc.detail.problem')}</h2><p class="big">{t(`${k}.problem`)}</p></section>
	<section><h2>{t('common.features')}</h2><BulletList items={list(`${k}.features`)} columns={2} /></section>
	<section><h2>{t('common.useCases')}</h2><BulletList items={list(`${k}.useCases`)} columns={2} /></section>
	<section><h2>{t('svc.detail.benefits')}</h2><BulletList items={list(`${k}.benefits`)} /></section>
	<section><h2>{t('svc.detail.integration')}</h2><p class="big">{t('svc.detail.integrationText')}</p></section>
	{#if service.id === 'monitoring'}<p class="note">{t(`${k}.note`)}</p>{/if}
	<section>
		<h2>{t('svc.detail.faq')}</h2>
		<div class="faq">
			{#each [0, 1] as i (i)}
				<details><summary>{faqItem(i).q}</summary><p>{faqItem(i).a}</p></details>
			{/each}
		</div>
	</section>
</div>

<CtaBand title={t('svc.final.title')}>
	<p>{t('svc.final.text')}</p>
	{#snippet actions()}
		<Button href={demoHref} size="lg">{t('common.demo')}</Button>
		<Button href={quoteHref([service.id])} size="lg" variant="outline" class="ghost-light">{t('common.quote')}</Button>
	{/snippet}
</CtaBand>

<style lang="scss">
	.body { padding: 3rem 0 5rem; display: grid; gap: 3rem; }
	.back { display: inline-flex; align-items: center; gap: 0.4rem; font-weight: 700; font-size: var(--fs-sm); }
	h2 { font-size: var(--fs-2xl); margin-bottom: 1.2rem; } .big { font-size: var(--fs-lg); color: var(--fg-muted); max-width: 70ch; }
	.note { padding: 1rem 1.2rem; background: var(--warning-bg); color: var(--warning); border-radius: var(--radius); font-weight: 600; font-size: var(--fs-sm); }
	.faq { display: grid; gap: 0.6rem; max-width: 780px; } details { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem 1.2rem; } summary { font-weight: 700; cursor: pointer; } details p { margin-top: 0.7rem; color: var(--fg-muted); }
</style>
