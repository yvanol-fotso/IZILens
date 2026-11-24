<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { BulletList, SectionHeader } from '$lib/components/shared';
	const { t, list } = getI18n();
</script>

<section class="lead">
	<div class="container wrap">
		<div>
			<SectionHeader title={t('about.leadership.title')} kicker={t('about.leadership.kicker')}><p>{t('about.leadership.text')}</p></SectionHeader>
			<p class="intro">{t('about.leadership.intro')}</p>
			<BulletList items={list('about.leadership.roles')} />
			<p class="note">{t('about.leadership.note')}</p>
		</div>
	</div>
</section>

<section class="amb">
	<div class="container">
		<p class="kick">{t('about.ambition.kicker')}</p>
		<h2>{t('about.ambition.title')}</h2>
		<p>{t('about.ambition.p1')}</p><p>{t('about.ambition.p2')}</p>
	</div>
</section>

<style lang="scss">
	.lead { padding: 5.5rem 0; background: var(--bg); } .intro { font-weight: 700; margin-bottom: 1rem; } .note { margin-top: 1.4rem; padding: 1rem 1.2rem; background: var(--info-bg); color: var(--info); border-radius: var(--radius); font-size: var(--fs-sm); font-weight: 600; max-width: 62ch; }
	.amb { padding: 5.5rem 0; background: var(--brand-navy); color: #fff; text-align: center; background-image: radial-gradient(50% 90% at 50% 100%, rgb(0 143 203 / 0.35), transparent 70%); .container { max-width: 780px; } .kick { color: var(--brand-cyan); font-style: italic; font-weight: 700; font-size: var(--fs-sm); } h2 { font-size: var(--fs-3xl); margin: 0.7rem 0 1.4rem; } p { color: #a9bfdc; font-size: var(--fs-lg); margin-bottom: 1rem; } }
</style>
