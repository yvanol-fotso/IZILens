<script lang="ts">
	import { reveal } from '$lib/actions/reveal';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Button, SectionHeader } from '$lib/components/shared';
	import Img from '$lib/components/shared/Img.svelte';
	const { t } = getI18n();
</script>

<section id="api" class="s">
	<div class="container wrap">
		<div use:reveal>
			<SectionHeader title={t('home.api.title')} tone="light"><p>{t('home.api.p1')}</p><p>{t('home.api.p2')}</p><p>{t('home.api.p3')}</p></SectionHeader>
			<div class="row">
				<Button href="/developers" size="lg">{t('home.api.primary')}</Button>
				<Button href="/developers#docs" size="lg" variant="outline" class="ghost-light">{t('home.api.secondary')}</Button>
			</div>
		</div>
		<!-- L'illustration contient déjà l'exemple d'appel POST /v1/kyc/verifications -->
		<div class="media" use:reveal={{ delay: 100 }}>
			<Img src="/marketing/home/developer-api" alt={t('home.images.api')} ratio="8/7" />
		</div>
	</div>
</section>

<style lang="scss">
	.s { padding: 6rem 0; background: var(--brand-navy); color: #fff; }
	.wrap { display: grid; grid-template-columns: 1.1fr 1fr; gap: 4rem; align-items: center; }
	.row { display: flex; gap: 0.8rem; flex-wrap: wrap; :global(.ghost-light) { color: #fff; border-color: rgb(255 255 255 / 0.3); &:hover { border-color: var(--brand-cyan) !important; color: var(--brand-cyan) !important; } } }
	.media { border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); border: 1px solid #16406b; overflow: hidden; }
	@media (max-width: 900px) { .wrap { grid-template-columns: 1fr; gap: 2.5rem; } }
</style>
