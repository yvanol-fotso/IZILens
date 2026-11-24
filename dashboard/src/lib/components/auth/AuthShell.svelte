<script lang="ts">
	import type { Snippet } from 'svelte';
	import { Check } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { LanguageSwitcher, Logo, ThemeToggle } from '$lib/components/shared';

	let { children }: { children: Snippet } = $props();
	const { t } = getI18n();
</script>

<div class="shell">
	<section class="form-side">
		<header><Logo /><div class="row"><LanguageSwitcher /><ThemeToggle /></div></header>
		<main id="main">{@render children()}</main>
		<footer><a href="/privacy">{t('footer.privacy')}</a><a href="/terms">{t('footer.terms')}</a></footer>
	</section>

	<aside class="brand" aria-hidden="false">
		<div class="inner">
			<h2>{t('auth.brand.title')}</h2>
			<ul>
				{#each ['one', 'two', 'three'] as k (k)}<li><Check size={18} />{t(`auth.brand.points.${k}`)}</li>{/each}
			</ul>
		</div>
		<span class="orb o1"></span><span class="orb o2"></span>
	</aside>
</div>

<style lang="scss">
	.shell { min-height: 100dvh; display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 0.9fr); }
	.form-side { display: flex; flex-direction: column; padding: 1.5rem clamp(1.25rem, 5vw, 4rem); header { display: flex; justify-content: space-between; align-items: center; } main { flex: 1; display: grid; align-content: center; width: min(100%, 420px); margin-inline: auto; padding: 2rem 0; } footer { display: flex; gap: 1.2rem; font-size: var(--fs-xs); a { color: var(--fg-muted); } } }
	.brand { position: relative; overflow: hidden; background: var(--brand-navy); color: #fff; display: grid; place-items: center; padding: 3rem; }
	.inner { position: relative; z-index: 1; max-width: 30rem; display: grid; gap: 2rem; h2 { font-size: var(--fs-3xl); } ul { display: grid; gap: 1rem; } li { display: flex; gap: 0.8rem; align-items: flex-start; color: #b8cae2; :global(svg) { color: var(--brand-cyan); margin-top: 4px; flex-shrink: 0; } } }
	.orb { position: absolute; border-radius: 50%; filter: blur(70px); &.o1 { width: 420px; height: 420px; background: rgb(34 199 242 / 0.3); top: -120px; right: -120px; } &.o2 { width: 380px; height: 380px; background: rgb(0 143 203 / 0.4); bottom: -140px; left: -100px; } }
	@media (max-width: 900px) { .shell { grid-template-columns: 1fr; } .brand { display: none; } }
</style>
