<script lang="ts">
	import { ArrowRight, ScanFace, FileCheck2, ShieldCheck, Fingerprint } from '@lucide/svelte';
	import { env } from '$env/dynamic/public';
	import { SITE } from '$lib/config/site';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Button } from '$lib/components/shared';

	const { t } = getI18n();
	const docsUrl = $derived(env.PUBLIC_DOCS_URL || '');
</script>

<section class="hero">
	<div class="grid-bg" aria-hidden="true"></div>
	<div class="container inner">
		<div class="copy">
			<h1>{t('home.hero.title')}</h1>
			<p class="sub">{t('home.hero.subtitle')}</p>
			<div class="ctas">
				<Button href="mailto:{SITE.email}" size="lg">
					{t('home.hero.primary')}
					{#snippet iconAfter()}<ArrowRight size={18} />{/snippet}
				</Button>
				{#if docsUrl}<Button href={docsUrl} size="lg" variant="outline" class="ghost-light">{t('home.hero.secondary')}</Button>{/if}
			</div>
		</div>

		<!-- Démo vivante : un dossier KYC qui se vérifie, une seule séquence orchestrée -->
		<div class="demo" aria-hidden="true">
			<div class="doc">
				<div class="doc-head"><span>{t('home.hero.demoTitle')}</span><em>{t('home.hero.demoScan')}</em></div>
				<div class="doc-body">
					<div class="photo">
						<svg viewBox="0 0 80 96"><circle cx="40" cy="34" r="17" /><path d="M8 96c0-19 14-31 32-31s32 12 32 31z" /></svg>
					</div>
					<div class="lines"><i style="width:82%"></i><i style="width:60%"></i><i style="width:74%"></i><i style="width:48%"></i><i style="width:66%"></i></div>
				</div>
				<div class="scan"></div>
				<span class="corner tl"></span><span class="corner tr"></span><span class="corner bl"></span><span class="corner br"></span>
			</div>
			<ul class="chips">
				<li style="--d: 1.1s"><FileCheck2 size={17} />{t('home.hero.demoDocument')}</li>
				<li style="--d: 1.9s"><Fingerprint size={17} />{t('home.hero.demoFace')}</li>
				<li style="--d: 2.7s"><ScanFace size={17} />{t('home.hero.demoLiveness')}</li>
				<li style="--d: 3.5s" class="final"><ShieldCheck size={17} />{t('home.hero.demoRisk')}</li>
			</ul>
		</div>
	</div>
</section>

<style lang="scss">
	.hero { position: relative; overflow: hidden; background: var(--brand-navy); color: #fff; padding: calc(var(--header-h) + 4.5rem) 0 6rem; isolation: isolate; }
	.hero::before { content: ''; position: absolute; inset: 0; z-index: -1; background: radial-gradient(55% 70% at 82% 20%, rgb(25 217 232 / 0.2), transparent 65%), radial-gradient(40% 60% at 5% 100%, rgb(8 124 245 / 0.28), transparent 70%); }
	.grid-bg { position: absolute; inset: 0; z-index: -1; opacity: 0.5; background-image: linear-gradient(rgb(255 255 255 / 0.05) 1px, transparent 1px), linear-gradient(90deg, rgb(255 255 255 / 0.05) 1px, transparent 1px); background-size: 56px 56px; mask-image: radial-gradient(70% 80% at 70% 40%, #000, transparent); }
	.inner { display: grid; grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr); gap: 4rem; align-items: center; }
	h1 { font-size: var(--fs-hero); letter-spacing: -0.04em; line-height: 1.02; max-width: 15ch; }
	.sub { margin-top: 1.5rem; font-size: var(--fs-lg); color: #a9bfdc; max-width: 46ch; line-height: 1.65; }
	.ctas { margin-top: 2.2rem; display: flex; gap: 0.8rem; flex-wrap: wrap; :global(.ghost-light) { color: #fff; border-color: rgb(255 255 255 / 0.3); &:hover { border-color: var(--brand-cyan) !important; color: var(--brand-cyan) !important; } } }

	.demo { position: relative; display: grid; gap: 1.1rem; justify-items: center; }
	.doc { position: relative; width: min(100%, 440px); aspect-ratio: 1.6; border-radius: 22px; background: linear-gradient(135deg, #12335f, #0b2447); border: 1px solid rgb(255 255 255 / 0.14); padding: 1.2rem 1.4rem; box-shadow: 0 40px 80px -30px rgb(0 0 0 / 0.7), 0 0 0 1px rgb(25 217 232 / 0.08); transform: rotate(-2.5deg); overflow: hidden; }
	.doc-head { display: flex; justify-content: space-between; font-size: 0.74rem; font-weight: 700; color: #9db8d9; em { font-style: normal; color: var(--brand-cyan); } }
	.doc-body { display: flex; gap: 1.1rem; margin-top: 1rem; }
	.photo { width: 28%; aspect-ratio: 0.82; background: #1b4577; border-radius: 12px; display: grid; place-items: end center; overflow: hidden; svg { width: 82%; fill: #7ea6d6; } }
	.lines { flex: 1; display: grid; gap: 0.7rem; align-content: start; padding-top: 0.2rem; i { display: block; height: 9px; border-radius: 5px; background: rgb(255 255 255 / 0.16); } }
	.scan { position: absolute; left: 0; right: 0; height: 64px; top: -64px; background: linear-gradient(180deg, transparent, rgb(25 217 232 / 0.4)); border-bottom: 2px solid var(--brand-cyan); animation: scan 3.4s ease-in-out 0.5s 2; }
	.corner { position: absolute; width: 22px; height: 22px; border: 3px solid var(--brand-cyan); &.tl { top: 10px; left: 10px; border-right: 0; border-bottom: 0; border-radius: 8px 0 0 0; } &.tr { top: 10px; right: 10px; border-left: 0; border-bottom: 0; border-radius: 0 8px 0 0; } &.bl { bottom: 10px; left: 10px; border-right: 0; border-top: 0; border-radius: 0 0 0 8px; } &.br { bottom: 10px; right: 10px; border-left: 0; border-top: 0; border-radius: 0 0 8px 0; } }
	.chips { display: flex; flex-wrap: wrap; gap: 0.6rem; justify-content: center; max-width: 460px; li { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.55rem 0.95rem; border-radius: var(--radius-pill); background: rgb(255 255 255 / 0.08); border: 1px solid rgb(255 255 255 / 0.14); font-size: var(--fs-sm); font-weight: 700; opacity: 0; transform: translateY(8px); animation: chip 0.5s var(--ease) var(--d) forwards; :global(svg) { color: var(--accent-mint); } &.final { background: var(--accent-mint); color: #032a1d; border-color: transparent; :global(svg) { color: #032a1d; } } } }
	@keyframes scan { 0% { top: -64px; } 100% { top: 100%; } }
	@keyframes chip { to { opacity: 1; transform: none; } }
	@media (max-width: 940px) { .inner { grid-template-columns: 1fr; gap: 3rem; } .hero { padding-bottom: 4rem; } .doc { transform: none; } }
	@media (prefers-reduced-motion: reduce) { .chips li { opacity: 1; transform: none; } .scan { display: none; } }
</style>
