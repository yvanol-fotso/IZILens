<script lang="ts">
	import { reveal } from '$lib/actions/reveal';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { SectionHeader } from '$lib/components/shared';
	const { t } = getI18n();
	const items = ['modularity', 'adaptability', 'integration', 'visibility', 'reach'];
</script>

<section class="s">
	<div class="container">
		<SectionHeader title={t('sol.why.title')} />
		<ul>{#each items as k, i (k)}<li use:reveal={{ delay: i * 60 }}><h3>{t(`sol.why.items.${k}.title`)}</h3><p>{t(`sol.why.items.${k}.desc`)}</p></li>{/each}</ul>
	</div>
</section>

<style lang="scss">
	.s { padding: 5.5rem 0; background: var(--bg); } ul { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 1rem; }
	li { padding: 1.4rem; border-top: 3px solid var(--brand-cyan); background: var(--surface); border-radius: 0 0 var(--radius) var(--radius); } h3 { font-size: var(--fs-lg); margin-bottom: 0.4rem; } p { color: var(--fg-muted); font-size: var(--fs-sm); }
</style>
