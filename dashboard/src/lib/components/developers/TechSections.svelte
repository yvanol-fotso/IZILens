<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Badge, BulletList, SectionHeader } from '$lib/components/shared';
	const { t, list } = getI18n();
</script>

<section class="s">
	<div class="container grid">
		<article><h2>{t('dev.sdk.title')}</h2><p>{t('dev.sdk.text')}</p><p class="note">{t('dev.sdk.note')}</p></article>
		<article><h2>{t('dev.webhooks.title')}</h2><p>{t('dev.webhooks.text')}</p><p class="ev">{t('dev.webhooks.eventsTitle')}</p><BulletList items={list('dev.webhooks.events')} /></article>
	</div>
</section>

<section id="docs" class="s alt">
	<div class="container">
		<SectionHeader title={t('dev.docs.title')}><p>{t('dev.docs.text')}</p></SectionHeader>
		<ul class="topics">{#each list('dev.docs.topics') as tp, i (tp)}<li><span>0{i + 1}</span>{tp}</li>{/each}</ul>
	</div>
</section>

<section class="s">
	<div class="container sec">
		<SectionHeader title={t('dev.security.title')} />
		<BulletList items={list('dev.security.list')} columns={2} />
	</div>
</section>

<style lang="scss">
	.s { padding: 5rem 0; background: var(--bg); &.alt { background: var(--bg-soft); border-block: 1px solid var(--border); } }
	.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; } h2 { font-size: var(--fs-2xl); margin-bottom: 1rem; } article p { color: var(--fg-muted); margin-bottom: 0.8rem; } .note { font-size: var(--fs-sm); font-style: italic; } .ev { font-weight: 800; color: var(--fg) !important; }
	.topics { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.7rem; li { display: flex; gap: 0.8rem; align-items: center; padding: 0.9rem 1.1rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); font-weight: 700; font-family: var(--font-mono); font-size: var(--fs-sm); span { color: var(--primary); } } }
	@media (max-width: 860px) { .grid { grid-template-columns: 1fr; } }
</style>
