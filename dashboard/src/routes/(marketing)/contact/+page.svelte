<script lang="ts">
	import { page } from '$app/state';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Confirmation, ContactCards, RequestForm } from '$lib/components/contact';
	import { Button, PageHero } from '$lib/components/shared';
	import { demoHref } from '$lib/config/services';

	let { data, form } = $props();
	const { t } = getI18n();
</script>

<svelte:head><title>{t('nav.contact')} · IZI LENS</title><meta name="description" content={t('contact.hero.text')} /></svelte:head>

<PageHero title={t('contact.hero.title')}>
	<p>{t('contact.hero.text')}</p>
	{#snippet actions()}
		<Button href="#form" size="lg">{t('contact.hero.primary')}</Button>
		<Button href={demoHref} size="lg" variant="outline" class="ghost-light">{t('contact.hero.secondary')}</Button>
	{/snippet}
</PageHero>

{#if form?.ok && form.reference}
	<div class="container done"><Confirmation reference={form.reference as string} /></div>
{:else}
	<ContactCards />
	<div class="container forms">
		<section id="form"><RequestForm kind="contact" {form} presetType={data.preset.type} presetServices={data.preset.services} /></section>
		<section id="demo"><RequestForm kind="demo" {form} presetServices={data.preset.type === 'demo' ? data.preset.services : []} /></section>
	</div>
{/if}

<section class="inst">
	<div class="container wrap">
		<div><h2>{t('contact.institutional.title')}</h2><p>{t('contact.institutional.text')}</p><p>{t('contact.institutional.hq')}</p></div>
		<div class="portal"><h3>{t('contact.portal.title')}</h3><p>{t('contact.portal.text')}</p><Button href="/login" variant="outline">{t('contact.cards.support.cta')}</Button></div>
	</div>
</section>

<style lang="scss">
	.forms { display: grid; grid-template-columns: 1.2fr 1fr; gap: 1.5rem; padding-bottom: 4rem; align-items: start; } .done { padding: 4rem 0; max-width: 760px; }
	.inst { padding: 3rem 0 5rem; } .wrap { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; } h2 { font-size: var(--fs-xl); } p { color: var(--fg-muted); margin-top: 0.4rem; }
	.portal { padding: 1.6rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); display: grid; gap: 0.6rem; justify-items: start; }
	@media (max-width: 1000px) { .forms, .wrap { grid-template-columns: 1fr; } }
</style>
