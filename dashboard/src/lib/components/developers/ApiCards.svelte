<script lang="ts">
	import { reveal } from '$lib/actions/reveal';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Badge, BulletList, SectionHeader } from '$lib/components/shared';
	const { t, list } = getI18n();
	const apis = ['kyc', 'kyb', 'bio', 'mon'];
</script>

<section class="s">
	<div class="container">
		<SectionHeader title={t('dev.apisTitle')}><p class="rule">{t('dev.publishRule')}</p></SectionHeader>
		<div class="grid">
			{#each apis as a, i (a)}
				<article use:reveal={{ delay: i * 70 }}>
					<div class="top"><h3>{t(`dev.apis.${a}.name`)}</h3><Badge tone="warning">{t('common.planned')}</Badge></div>
					<p class="tag">{t(`dev.apis.${a}.tag`)}</p>
					<p>{t(`dev.apis.${a}.desc`)}</p>
					<BulletList items={list(`dev.apis.${a}.list`)} />
				</article>
			{/each}
		</div>
	</div>
</section>

<style lang="scss">
	.s { padding: 5.5rem 0; background: var(--bg); } .rule { font-size: var(--fs-sm) !important; }
	.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 1rem; }
	article { display: grid; gap: 0.7rem; align-content: start; padding: 1.8rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); }
	.top { display: flex; justify-content: space-between; gap: 0.5rem; align-items: center; } h3 { font-size: var(--fs-xl); font-family: var(--font-mono); letter-spacing: -0.02em; }
	.tag { color: var(--primary); font-weight: 700; font-size: var(--fs-sm); } article p { color: var(--fg-muted); font-size: var(--fs-sm); } :global(article li) { font-size: var(--fs-sm); }
</style>
