<script lang="ts">
	import { Lock } from '@lucide/svelte';
	import { reveal } from '$lib/actions/reveal';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { BulletList } from '$lib/components/shared';
	const { t, list } = getI18n();
</script>

<section id="security" class="s">
	<div class="container wrap">
		<div class="copy" use:reveal>
			<span class="ico"><Lock size={28} /></span>
			<h2>{t('home.security.title')}</h2>
			<p class="lead">{t('home.security.lead')}</p>
			<p>{t('home.security.text')}</p>
		</div>
		<div class="list" use:reveal={{ delay: 100 }}>
			<p class="intro">{t('home.security.intro')}</p>
			<BulletList items={list('home.security.points')} />
			<p class="closing">{t('home.security.closing')}</p>
		</div>
	</div>
</section>

<style lang="scss">
	.s { padding: 6rem 0; background: var(--bg-soft); border-block: 1px solid var(--border); }
	.wrap { display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: center; }
	.ico { width: 58px; height: 58px; border-radius: 18px; display: grid; place-items: center; background: var(--brand-navy); color: var(--brand-cyan); margin-bottom: 1.2rem; }
	h2 { font-size: var(--fs-3xl); } .lead { font-size: var(--fs-lg); font-weight: 700; margin: 1rem 0 0.6rem; } .copy p { color: var(--fg-muted); }
	.list { display: grid; gap: 1rem; padding: 1.8rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); } .intro { font-weight: 700; }
	.closing { font-weight: 800; color: var(--primary); padding-top: 0.5rem; border-top: 1px solid var(--border); }
	@media (max-width: 900px) { .wrap { grid-template-columns: 1fr; gap: 2rem; } }
</style>
