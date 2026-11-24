<script lang="ts">
	import { reveal } from '$lib/actions/reveal';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { SectionHeader } from '$lib/components/shared';
	const i18n = getI18n();
	const { t } = i18n;
	const items = Array.from({ length: 8 }, (_, i) => i);
	const get = (i: number, f: 'n' | 'd') => translate(i18n.locale, `about.eco.items.${i}.${f}`);
	import { translate } from '$lib/i18n/translate';
</script>

<section class="s">
	<div class="container">
		<SectionHeader title={t('about.eco.title')} kicker={t('about.eco.kicker')}><p>{t('about.eco.text')}</p></SectionHeader>
		<div class="grid">
			{#each items as i (i)}
				<article class:me={get(i, 'n') === 'IZI LENS'} use:reveal={{ delay: (i % 4) * 60 }}><h3>{get(i, 'n')}</h3><p>{get(i, 'd')}</p></article>
			{/each}
		</div>
	</div>
</section>

<style lang="scss">
	.s { padding: 5.5rem 0; background: var(--bg-soft); border-block: 1px solid var(--border); } .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; }
	article { padding: 1.6rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); display: grid; gap: 0.5rem; align-content: start; &.me { background: var(--brand-navy); color: #fff; border: 0; p { color: #a9bfdc; } h3 { color: var(--brand-cyan); } } }
	h3 { font-size: var(--fs-md); letter-spacing: 0.02em; } p { color: var(--fg-muted); font-size: var(--fs-sm); }
</style>
