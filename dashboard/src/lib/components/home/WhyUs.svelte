<script lang="ts">
	import { ShieldAlert, Globe, Zap, SlidersHorizontal, Scale } from '@lucide/svelte';
	import { reveal } from '$lib/actions/reveal';
	import { getI18n } from '$lib/i18n/index.svelte';

	const { t } = getI18n();
	const items = [
		{ key: 'fraud', icon: ShieldAlert, big: true },
		{ key: 'coverage', icon: Globe },
		{ key: 'speed', icon: Zap },
		{ key: 'flexible', icon: SlidersHorizontal },
		{ key: 'compliance', icon: Scale, wide: true }
	];
</script>

<section id="why" class="section">
	<div class="container">
		<header use:reveal>
			<h2>{t('home.why.title')}</h2>
			<p>{t('home.why.subtitle')}</p>
		</header>
		<div class="bento">
			{#each items as it, i (it.key)}
				{@const Icon = it.icon}
				<article class:big={it.big} class:wide={it.wide} use:reveal={{ delay: i * 60 }}>
					<span class="ico"><Icon size={it.big ? 30 : 24} /></span>
					<h3>{t(`home.why.items.${it.key}.title`)}</h3>
					<p>{t(`home.why.items.${it.key}.desc`)}</p>
				</article>
			{/each}
		</div>
	</div>
</section>

<style lang="scss">
	.section { padding: 6rem 0; background: var(--bg); }
	header { max-width: 640px; margin-bottom: 3rem; h2 { font-size: var(--fs-3xl); } p { margin-top: 1rem; color: var(--fg-muted); font-size: var(--fs-lg); } }
	.bento { display: grid; grid-template-columns: repeat(6, 1fr); gap: 1rem; }
	article { grid-column: span 2; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1.8rem; display: grid; gap: 0.6rem; align-content: start;
		&.big { grid-column: span 3; grid-row: span 2; background: var(--brand-navy); color: #fff; border: 0; background-image: radial-gradient(80% 60% at 100% 0%, rgb(25 217 232 / 0.25), transparent 60%); padding: 2.4rem; h3 { font-size: var(--fs-2xl); max-width: 14ch; } p { color: #a9bfdc; font-size: var(--fs-lg); max-width: 34ch; } .ico { background: var(--brand-cyan); color: var(--brand-navy); } }
		&.wide { grid-column: span 3; }
		&:not(.big):nth-child(2) { grid-column: span 3; }
	}
	.ico { width: 52px; height: 52px; border-radius: 16px; display: grid; place-items: center; background: var(--primary-soft); color: var(--primary); margin-bottom: 0.6rem; }
	h3 { font-size: var(--fs-lg); }
	article p { color: var(--fg-muted); font-size: var(--fs-sm); }
	@media (max-width: 900px) { .bento { grid-template-columns: 1fr; } article, article.big, article.wide, article:not(.big):nth-child(2) { grid-column: auto; grid-row: auto; } }
</style>
