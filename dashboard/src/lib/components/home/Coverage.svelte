<script lang="ts">
	import { BookUser, Briefcase, CarFront, Globe2, IdCard } from '@lucide/svelte';
	import { reveal } from '$lib/actions/reveal';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Button } from '$lib/components/shared';
	import { SITE } from '$lib/config/site';

	const { t } = getI18n();
	const docs = [
		{ key: 'passports', icon: BookUser, color: 'var(--primary)' },
		{ key: 'ids', icon: IdCard, color: 'var(--accent-mint)' },
		{ key: 'licenses', icon: CarFront, color: 'var(--accent-purple)' },
		{ key: 'permits', icon: Globe2, color: 'var(--accent-rose)' },
		{ key: 'business', icon: Briefcase, color: 'var(--accent-orange)' }
	];
	const stats = ['countries', 'docs', 'compliance', 'speed'];
</script>

<section id="coverage" class="section">
	<div class="container wrap">
		<div class="left" use:reveal>
			<h2>{t('home.coverage.title')}</h2>
			<p>{t('home.coverage.subtitle')}</p>
			<dl>
				{#each stats as s (s)}
					<div><dt>{t(`home.coverage.stats.${s}.value`)}</dt><dd>{t(`home.coverage.stats.${s}.label`)}</dd></div>
				{/each}
			</dl>
			<Button href="mailto:{SITE.email}" variant="brand">{t('home.hero.primary')}</Button>
		</div>
		<ul class="docs">
			{#each docs as d, i (d.key)}
				{@const Icon = d.icon}
				<li style:--c={d.color} use:reveal={{ delay: i * 60 }}>
					<span class="ico"><Icon size={22} /></span>
					<div><h3>{t(`home.coverage.docs.${d.key}.title`)}</h3><p>{t(`home.coverage.docs.${d.key}.desc`)}</p></div>
				</li>
			{/each}
		</ul>
	</div>
</section>

<style lang="scss">
	.section { padding: 6rem 0; background: var(--bg-soft); border-block: 1px solid var(--border); }
	.wrap { display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: center; }
	h2 { font-size: var(--fs-3xl); }
	.left > p { margin: 1rem 0 2rem; color: var(--fg-muted); font-size: var(--fs-lg); max-width: 48ch; }
	dl { display: grid; grid-template-columns: 1fr 1fr; gap: 1.6rem 2rem; margin: 0 0 2.2rem; div { border-left: 3px solid var(--brand-cyan); padding-left: 1rem; } dt { font-size: 1.9rem; font-weight: 800; letter-spacing: -0.03em; line-height: 1.1; } dd { margin: 0.2rem 0 0; color: var(--fg-muted); font-size: var(--fs-sm); } }
	.docs { display: grid; gap: 0.7rem; li { display: flex; gap: 1rem; align-items: center; padding: 1rem 1.2rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); transition: transform 0.2s var(--ease), border-color 0.2s; &:nth-child(odd) { margin-right: 2rem; } &:nth-child(even) { margin-left: 2rem; } &:hover { border-color: var(--c); } } .ico { width: 46px; height: 46px; border-radius: 14px; display: grid; place-items: center; background: color-mix(in srgb, var(--c) 14%, var(--surface)); color: var(--c); flex-shrink: 0; } h3 { font-size: var(--fs-md); } p { color: var(--fg-muted); font-size: var(--fs-sm); } }
	@media (max-width: 900px) { .wrap { grid-template-columns: 1fr; gap: 2.5rem; } .docs li:nth-child(n) { margin: 0; } }
</style>
