<script lang="ts">
	import { ArrowRight } from '@lucide/svelte';
	import { reveal } from '$lib/actions/reveal';
	import { SERVICES, quoteHref } from '$lib/config/services';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Button, SectionHeader, ServicePicker } from '$lib/components/shared';
	import Img from '$lib/components/shared/Img.svelte';

	const { t } = getI18n();
	let selected = $state<string[]>([]);
</script>

<section id="services" class="s">
	<div class="container">
		<SectionHeader title={t('home.services.title')}><p>{t('home.services.text')}</p></SectionHeader>
		<figure class="banner" use:reveal>
			<Img src="/marketing/home/services-modules" alt={t('home.images.services')} ratio="1200/380" />
		</figure>
		<div class="cards">
			{#each SERVICES as s, i (s.id)}
				{@const Icon = s.icon}
				<a class="card" href="/services/{s.slug}" style:--c={s.color} use:reveal={{ delay: i * 70 }}>
					<span class="ico"><Icon size={26} /></span>
					<h3>{t(`svc.items.${s.id}.code`)}<small>{t(`svc.items.${s.id}.name`)}</small></h3>
					<p>{t(`svc.items.${s.id}.short`)}</p>
					<span class="more">{t('common.learnMore')}<ArrowRight size={16} /></span>
				</a>
			{/each}
		</div>
		<div class="compose">
			<ServicePicker bind:selected />
			<div class="row">
				<Button href={quoteHref(selected)} variant="brand" size="lg">{t('home.services.button')}</Button>
				{#if selected.length}<span class="muted">{t('common.selected', { count: selected.length })}</span>{/if}
			</div>
		</div>
	</div>
</section>

<style lang="scss">
	.s { padding: 6rem 0; background: var(--bg-soft); border-block: 1px solid var(--border); }
	.banner { margin: 0 0 2.5rem; border-radius: var(--radius-lg); box-shadow: var(--shadow-md); }
	.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; }
	.card { display: grid; gap: 0.7rem; align-content: start; padding: 1.7rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); color: var(--fg); text-decoration: none !important; transition: transform 0.2s var(--ease), border-color 0.2s, box-shadow 0.2s; &:hover { transform: translateY(-4px); border-color: var(--c); box-shadow: var(--shadow-md); } }
	.ico { width: 56px; height: 56px; border-radius: 17px; display: grid; place-items: center; background: color-mix(in srgb, var(--c) 14%, var(--surface)); color: var(--c); }
	h3 { font-size: var(--fs-xl); display: grid; small { font-size: var(--fs-xs); font-weight: 600; color: var(--fg-muted); letter-spacing: 0; margin-top: 0.2rem; } }
	p { color: var(--fg-muted); font-size: var(--fs-sm); }
	.more { display: inline-flex; align-items: center; gap: 0.4rem; font-weight: 700; color: var(--primary); font-size: var(--fs-sm); margin-top: 0.4rem; }
	.compose { margin-top: 3rem; padding: 1.6rem; background: var(--surface); border: 1px dashed var(--border-strong); border-radius: var(--radius-lg); display: grid; gap: 1.2rem; }
</style>
