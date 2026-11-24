<script lang="ts">
	import { reveal } from '$lib/actions/reveal';
	import { getI18n } from '$lib/i18n/index.svelte';
	const { t, list } = getI18n();
</script>

<section class="s">
	<div class="container wrap">
		<h2 use:reveal>{t('about.hero.title')}</h2>
		<div class="cols" use:reveal={{ delay: 80 }}>{#each list('about.story') as p, i (i)}<p class:last={i === 5}>{p}</p>{/each}</div>
	</div>
</section>

<style lang="scss">
	.s { padding: 5.5rem 0; background: var(--bg); } .wrap { display: grid; grid-template-columns: 1fr 1.3fr; gap: 4rem; align-items: start; }
	h2 { font-size: var(--fs-3xl); position: sticky; top: calc(var(--header-h) + 24px); } .cols { display: grid; gap: 1.2rem; color: var(--fg-muted); font-size: var(--fs-lg); line-height: 1.75; } .last { color: var(--fg); font-weight: 700; padding-left: 1.2rem; border-left: 4px solid var(--brand-cyan); }
	@media (max-width: 900px) { .wrap { grid-template-columns: 1fr; gap: 1.8rem; } h2 { position: static; } }
</style>
