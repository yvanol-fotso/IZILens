<script lang="ts">
	import { Blocks, Sparkles, Plug, Eye, ShieldCheck, Globe2 } from '@lucide/svelte';
	import { reveal } from '$lib/actions/reveal';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { SectionHeader } from '$lib/components/shared';

	const { t } = getI18n();
	const items = [
		{ k: 'modular', icon: Blocks, big: true }, { k: 'simple', icon: Sparkles }, { k: 'integrable', icon: Plug },
		{ k: 'visibility', icon: Eye }, { k: 'security', icon: ShieldCheck }, { k: 'international', icon: Globe2 }
	];
</script>

<section id="why" class="s">
	<div class="container">
		<SectionHeader title={t('home.why.title')} />
		<div class="bento">
			{#each items as it, i (it.k)}
				{@const Icon = it.icon}
				<article class:big={it.big} use:reveal={{ delay: i * 60 }}>
					<span class="ico"><Icon size={it.big ? 30 : 24} /></span>
					<h3>{t(`home.why.items.${it.k}.title`)}</h3>
					<p>{t(`home.why.items.${it.k}.desc`)}</p>
				</article>
			{/each}
		</div>
	</div>
</section>

<style lang="scss">
	.s { padding: 6rem 0; background: var(--bg); }
	.bento { display: grid; grid-template-columns: repeat(6, 1fr); gap: 1rem; }
	article { grid-column: span 2; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1.8rem; display: grid; gap: 0.6rem; align-content: start;
		&.big { grid-column: span 3; grid-row: span 2; background: var(--brand-navy); color: #fff; border: 0; background-image: radial-gradient(80% 60% at 100% 0%, rgb(34 199 242 / 0.28), transparent 60%); padding: 2.4rem; h3 { font-size: var(--fs-2xl); max-width: 14ch; } p { color: #a9bfdc; font-size: var(--fs-lg); max-width: 34ch; } .ico { background: var(--brand-cyan); color: var(--brand-navy); } }
		&:nth-child(2) { grid-column: span 3; } }
	.ico { width: 52px; height: 52px; border-radius: 16px; display: grid; place-items: center; background: var(--primary-soft); color: var(--primary); margin-bottom: 0.6rem; }
	h3 { font-size: var(--fs-lg); } article p { color: var(--fg-muted); font-size: var(--fs-sm); }
	@media (max-width: 900px) { .bento { grid-template-columns: 1fr; } article, article.big, article:nth-child(2) { grid-column: auto; grid-row: auto; } }
</style>
