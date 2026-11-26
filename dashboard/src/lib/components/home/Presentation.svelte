<script lang="ts">
	import { reveal } from '$lib/actions/reveal';
	import { getI18n } from '$lib/i18n/index.svelte';
	import Img from '$lib/components/shared/Img.svelte';
	const { t } = getI18n();
</script>

<section class="s">
	<div class="container wrap">
		<div class="left">
			<h2 use:reveal>{t('home.intro.title')}</h2>
			<div class="media" use:reveal={{ delay: 120 }}>
				<Img src="/marketing/home/presentation" alt={t('home.images.presentation')} ratio="8/7" />
			</div>
		</div>
		<div class="cols" use:reveal={{ delay: 80 }}>
			<p>{t('home.intro.p1')}</p>
			<p>{t('home.intro.p2')}</p>
			<p>{t('home.intro.p3')}</p>
			<p class="ambition">{t('home.intro.p4')}</p>
		</div>
	</div>
</section>

<style lang="scss">
	.s { padding: 6rem 0; background: var(--bg); }
	.wrap { display: grid; grid-template-columns: 1fr 1.2fr; gap: 4rem; align-items: start; }
	.left { display: grid; gap: 2rem; position: sticky; top: calc(var(--header-h) + 24px); }
	h2 { font-size: var(--fs-3xl); }
	.media { --img-radius: var(--radius-lg); box-shadow: var(--shadow-md); border-radius: var(--radius-lg); }
	.cols { display: grid; gap: 1.2rem; font-size: var(--fs-lg); color: var(--fg-muted); line-height: 1.75; }
	.ambition { color: var(--fg); font-weight: 700; padding-left: 1.2rem; border-left: 4px solid var(--brand-cyan); }
	@media (max-width: 900px) { .wrap { grid-template-columns: 1fr; gap: 1.8rem; } .left { position: static; } }
</style>
