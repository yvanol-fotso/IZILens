<script lang="ts">
	import { reveal } from '$lib/actions/reveal';
	import { quoteHref } from '$lib/config/services';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { BulletList, Button, SectionHeader } from '$lib/components/shared';
	const { t, list } = getI18n();
</script>

<section id="pricing" class="s">
	<div class="container wrap">
		<div use:reveal>
			<SectionHeader title={t('home.pricing.title')}><p>{t('home.pricing.p1')}</p><p>{t('home.pricing.p2')}</p><p>{t('home.pricing.p3')}</p></SectionHeader>
		</div>
		<div class="box" use:reveal={{ delay: 100 }}>
			<p class="intro">{t('home.pricing.intro')}</p>
			<BulletList items={list('home.pricing.points')} />
			<div class="row">
				<Button href={quoteHref()} variant="brand">{t('home.pricing.primary')}</Button>
				<Button href={quoteHref()} variant="outline">{t('home.pricing.secondary')}</Button>
			</div>
		</div>
	</div>
</section>

<style lang="scss">
	.s { padding: 6rem 0; background: var(--bg); }
	.wrap { display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: center; }
	.box { display: grid; gap: 1.2rem; padding: 2rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-xl); box-shadow: var(--shadow-md); } .intro { font-weight: 800; }
	@media (max-width: 900px) { .wrap { grid-template-columns: 1fr; gap: 2rem; } }
</style>
