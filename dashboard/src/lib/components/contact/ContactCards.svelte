<script lang="ts">
	import { Briefcase, Handshake, Presentation, LifeBuoy } from '@lucide/svelte';
	import { reveal } from '$lib/actions/reveal';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Button, SectionHeader } from '$lib/components/shared';
	const { t } = getI18n();
	const cards = [
		{ k: 'sales', icon: Briefcase, href: '/contact?type=sales#form', color: 'var(--brand-blue)' },
		{ k: 'partners', icon: Handshake, href: '/contact?type=partnership#form', color: 'var(--accent-purple)' },
		{ k: 'demo', icon: Presentation, href: '/contact?type=demo#demo', color: 'var(--accent-mint)' },
		{ k: 'support', icon: LifeBuoy, href: '/login', color: 'var(--accent-orange)' }
	];
</script>

<section class="s">
	<div class="container">
		<SectionHeader title={t('contact.cardsTitle')} />
		<div class="grid">
			{#each cards as c, i (c.k)}
				{@const Icon = c.icon}
				<article style:--c={c.color} use:reveal={{ delay: i * 60 }}>
					<span class="ico"><Icon size={24} /></span>
					<h3>{t(`contact.cards.${c.k}.title`)} <small>{t(`contact.cards.${c.k}.tag`)}</small></h3>
					<p>{t(`contact.cards.${c.k}.desc`)}</p>
					<Button href={c.href} variant="outline" size="sm">{t(`contact.cards.${c.k}.cta`)}</Button>
				</article>
			{/each}
		</div>
	</div>
</section>

<style lang="scss">
	.s { padding: 5rem 0 3rem; background: var(--bg); } .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; }
	article { display: grid; gap: 0.7rem; align-content: start; justify-items: start; padding: 1.7rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); border-top: 4px solid var(--c); }
	.ico { width: 50px; height: 50px; border-radius: 15px; display: grid; place-items: center; background: color-mix(in srgb, var(--c) 14%, var(--surface)); color: var(--c); }
	h3 { font-size: var(--fs-lg); small { display: block; font-size: var(--fs-xs); color: var(--fg-muted); font-weight: 600; letter-spacing: 0; } } p { color: var(--fg-muted); font-size: var(--fs-sm); flex: 1; }
</style>
