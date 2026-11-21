<script lang="ts">
	import { ArrowRight, Rocket, Settings, Headset, ShieldCheck } from '@lucide/svelte';
	import { env } from '$env/dynamic/public';
	import { reveal } from '$lib/actions/reveal';
	import { SITE } from '$lib/config/site';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Button } from '$lib/components/shared';

	const { t } = getI18n();
	const docsUrl = $derived(env.PUBLIC_DOCS_URL || '');
	const perks = [
		{ key: 'onboarding', icon: Rocket },
		{ key: 'integration', icon: Settings },
		{ key: 'support', icon: Headset },
		{ key: 'partner', icon: ShieldCheck }
	];
</script>

<section id="developers" class="cta">
	<div class="container" use:reveal>
		<div class="main">
			<h2>{t('home.cta.title')}</h2>
			<p>{t('home.cta.subtitle')}</p>
			<div class="btns">
				<Button href="mailto:{SITE.email}" size="lg">
					{t('home.cta.primary')}
					{#snippet iconAfter()}<ArrowRight size={18} />{/snippet}
				</Button>
				{#if docsUrl}<Button href={docsUrl} size="lg" variant="outline" class="ghost-light">{t('home.cta.secondary')}</Button>{/if}
			</div>
		</div>
		<ul>
			{#each perks as p (p.key)}
				{@const Icon = p.icon}
				<li><Icon size={22} /><div><h3>{t(`home.cta.perks.${p.key}.title`)}</h3><p>{t(`home.cta.perks.${p.key}.desc`)}</p></div></li>
			{/each}
		</ul>
	</div>
</section>

<style lang="scss">
	.cta { background: var(--brand-navy); color: #fff; padding: 5.5rem 0; background-image: radial-gradient(50% 90% at 0% 100%, rgb(8 124 245 / 0.35), transparent 70%), radial-gradient(40% 70% at 100% 0%, rgb(25 217 232 / 0.18), transparent 70%); }
	.container { display: grid; grid-template-columns: 1.2fr 1fr; gap: 4rem; align-items: center; }
	h2 { font-size: var(--fs-3xl); max-width: 16ch; }
	.main p { margin: 1rem 0 2rem; color: #a9bfdc; font-size: var(--fs-lg); max-width: 46ch; }
	.btns { display: flex; gap: 0.8rem; flex-wrap: wrap; :global(.ghost-light) { color: #fff; border-color: rgb(255 255 255 / 0.3); &:hover { border-color: var(--brand-cyan) !important; color: var(--brand-cyan) !important; } } }
	ul { display: grid; gap: 1.2rem; }
	li { display: flex; gap: 1rem; align-items: flex-start; padding-bottom: 1.2rem; border-bottom: 1px solid rgb(255 255 255 / 0.1); &:last-child { border: 0; padding: 0; } :global(svg) { color: var(--brand-cyan); flex-shrink: 0; margin-top: 3px; } h3 { font-size: var(--fs-md); } p { color: #9db4d1; font-size: var(--fs-sm); } }
	@media (max-width: 900px) { .container { grid-template-columns: 1fr; gap: 2.5rem; } }
</style>
