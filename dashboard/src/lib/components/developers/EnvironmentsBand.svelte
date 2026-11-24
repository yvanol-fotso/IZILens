<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { BulletList, SectionHeader } from '$lib/components/shared';
	const { t, list } = getI18n();
</script>

<section class="s">
	<div class="container">
		<SectionHeader title={t('dev.env.title')} />
		<div class="two">
			<article class="sand"><h3>{t('dev.env.sandbox.name')}</h3><p>{t('dev.env.sandbox.desc')}</p><BulletList items={list('dev.env.sandbox.list')} /></article>
			<article class="prod"><h3>{t('dev.env.prod.name')}</h3><p>{t('dev.env.prod.desc')}</p><BulletList items={list('dev.env.prod.list')} /></article>
		</div>
		<p class="note">{t('dev.env.note')}</p>
	</div>
</section>

<style lang="scss">
	.s { padding: 5.5rem 0; background: var(--bg); } .two { display: grid; grid-template-columns: 1fr 1fr; gap: 1.2rem; }
	article { display: grid; gap: 0.8rem; align-content: start; padding: 1.9rem; border-radius: var(--radius-lg); border: 1px solid var(--border); background: var(--surface); border-top: 5px solid var(--accent-orange); &.prod { border-top-color: var(--accent-mint); } }
	h3 { font-size: var(--fs-xl); } p { color: var(--fg-muted); font-size: var(--fs-sm); } .note { margin-top: 1.4rem; color: var(--fg-muted); font-size: var(--fs-sm); }
	@media (max-width: 800px) { .two { grid-template-columns: 1fr; } }
</style>
