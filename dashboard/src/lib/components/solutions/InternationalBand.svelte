<script lang="ts">
	import { Globe2 } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Button } from '$lib/components/shared';
	const { t } = getI18n();
</script>

<section class="s">
	<div class="container wrap">
		<div class="globe" aria-hidden="true"><Globe2 size={120} strokeWidth={1} /></div>
		<div>
			<p class="kick">{t('sol.intl.kicker')}</p>
			<h2>{t('sol.intl.title')}</h2>
			<p>{t('sol.intl.p1')}</p><p>{t('sol.intl.p2')}</p><p>{t('sol.intl.p3')}</p>
			<div class="row"><Button href="/services">{t('sol.intl.primary')}</Button><Button href="/contact#form" variant="outline" class="ghost-light">{t('sol.intl.secondary')}</Button></div>
		</div>
	</div>
</section>

<style lang="scss">
	.s { padding: 5.5rem 0; background: var(--brand-navy); color: #fff; } .wrap { display: grid; grid-template-columns: 0.6fr 1.4fr; gap: 3.5rem; align-items: center; }
	.globe { aspect-ratio: 1; max-width: 260px; border-radius: 50%; display: grid; place-items: center; color: var(--brand-cyan); background: radial-gradient(circle at 30% 30%, rgb(34 199 242 / 0.25), transparent 70%); border: 1px solid rgb(255 255 255 / 0.15); }
	.kick { color: var(--brand-cyan); font-style: italic; font-weight: 700; font-size: var(--fs-sm); } h2 { font-size: var(--fs-3xl); margin: 0.6rem 0 1rem; } p { color: #a9bfdc; margin-bottom: 0.8rem; } .row { margin-top: 1.4rem; :global(.ghost-light) { color: #fff; border-color: rgb(255 255 255 / 0.3); } }
	@media (max-width: 900px) { .wrap { grid-template-columns: 1fr; } .globe { max-width: 160px; } }
</style>
