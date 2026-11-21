<script lang="ts">
	import { ChevronDown, Menu, X, ArrowRight } from '@lucide/svelte';
	import { page } from '$app/state';
	import { env } from '$env/dynamic/public';
	import { clickOutside } from '$lib/actions/clickOutside';
	import { focusTrap } from '$lib/actions/focusTrap';
	import { marketingNav, solutionGroups } from '$lib/config/navigation';
	import { SITE } from '$lib/config/site';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { mobileNavOpen } from '$lib/stores/ui';
	import { Button, LanguageSwitcher, Logo, ThemeToggle } from '$lib/components/shared';

	const { t } = getI18n();
	let solutionsOpen = $state(false);
	let scrolled = $state(false);
	const user = $derived(page.data.user);
	const docsUrl = $derived(env.PUBLIC_DOCS_URL || '');
	const links = marketingNav.filter((l) => l.enabled);

	$effect(() => {
		const onScroll = () => (scrolled = window.scrollY > 8);
		onScroll();
		window.addEventListener('scroll', onScroll, { passive: true });
		return () => window.removeEventListener('scroll', onScroll);
	});
	$effect(() => {
		void page.url.pathname;
		void page.url.hash;
		$mobileNavOpen = false;
		solutionsOpen = false;
	});
</script>

<header class="nav" class:scrolled>
	<div class="container bar">
		<Logo tone="light" size={38} />

		<nav class="links" aria-label="Main">
			{#each links.slice(0, 1) as l (l.key)}<a href={l.href} aria-current={page.url.pathname + page.url.hash === l.href ? 'page' : undefined}>{t(`nav.${l.key}`)}</a>{/each}

			<div class="dd" use:clickOutside={() => (solutionsOpen = false)}>
				<button type="button" class="dd-btn" aria-expanded={solutionsOpen} onclick={() => (solutionsOpen = !solutionsOpen)}>
					{t('nav.solutions')}<ChevronDown size={16} />
				</button>
				{#if solutionsOpen}
					<div class="mega">
						{#each solutionGroups as g (g.key)}
							<div class="col">
								<h3>{t(`solutions.groups.${g.key}`)}</h3>
								{#each g.items as it (it.key)}
									{@const Icon = it.icon}
									<a href={it.href}><span class="i"><Icon size={17} /></span>{t(`solutions.items.${it.key}`)}</a>
								{/each}
							</div>
						{/each}
					</div>
				{/if}
			</div>

			{#each links.slice(1) as l (l.key)}<a href={l.href}>{t(`nav.${l.key}`)}</a>{/each}
			{#if docsUrl}<a href={docsUrl}>{t('nav.developers')}</a>{/if}
		</nav>

		<div class="right">
			<LanguageSwitcher variant="light" />
			<ThemeToggle variant="light" />
			{#if user}
				<Button href="/app" size="sm" class="cta">{t('nav.openApp')}</Button>
			{:else}
				<a class="signin" href="/login">{t('nav.signIn')}</a>
				<Button href="mailto:{SITE.email}" size="sm" class="cta">
					{t('nav.contactSales')}
					{#snippet iconAfter()}<ArrowRight size={16} />{/snippet}
				</Button>
			{/if}
			<button type="button" class="burger" onclick={() => ($mobileNavOpen = true)} aria-label={t('nav.menu')} aria-expanded={$mobileNavOpen} aria-controls="mobile-nav"><Menu size={22} /></button>
		</div>
	</div>
</header>

{#if $mobileNavOpen}
	<div class="drawer-scrim" role="presentation" onclick={() => ($mobileNavOpen = false)}></div>
	<div id="mobile-nav" class="drawer" role="dialog" aria-modal="true" use:focusTrap aria-label={t('nav.menu')}>
		<div class="d-head">
			<Logo tone="light" size={34} />
			<button type="button" onclick={() => ($mobileNavOpen = false)} aria-label={t('common.close')}><X size={22} /></button>
		</div>
		<nav>
			{#each links as l (l.key)}<a href={l.href}>{t(`nav.${l.key}`)}</a>{/each}
			{#if docsUrl}<a href={docsUrl}>{t('nav.developers')}</a>{/if}
			{#each solutionGroups as g (g.key)}
				<h3>{t(`solutions.groups.${g.key}`)}</h3>
				{#each g.items as it (it.key)}<a class="sub" href={it.href}>{t(`solutions.items.${it.key}`)}</a>{/each}
			{/each}
		</nav>
		<div class="d-foot">
			<div class="row"><LanguageSwitcher variant="light" /><ThemeToggle variant="light" /></div>
			{#if user}
				<Button href="/app" block>{t('nav.openApp')}</Button>
			{:else}
				<Button href="/login" variant="outline" block class="on-dark">{t('nav.signIn')}</Button>
				<Button href="mailto:{SITE.email}" block>{t('nav.contactSales')}</Button>
			{/if}
		</div>
	</div>
{/if}

<style lang="scss">
	.nav { position: fixed; inset: 0 0 auto 0; z-index: var(--z-nav); height: var(--header-h); color: #fff; transition: background 0.25s, box-shadow 0.25s, backdrop-filter 0.25s; &.scrolled { background: rgb(16 30 45 / 0.86); backdrop-filter: blur(14px) saturate(1.4); box-shadow: 0 1px 0 rgb(255 255 255 / 0.07); } }
	.bar { height: 100%; display: flex; align-items: center; gap: 2rem; }
	.links { display: flex; align-items: center; gap: 0.25rem; flex: 1; a, .dd-btn { color: #d3e2f6; font-weight: 600; font-size: var(--fs-sm); padding: 0.55rem 0.8rem; border-radius: var(--radius-sm); background: none; border: 0; display: inline-flex; align-items: center; gap: 0.3rem; &:hover { color: #fff; background: rgb(255 255 255 / 0.08); text-decoration: none; } } }
	.dd { position: relative; }
	.mega { position: absolute; top: calc(100% + 12px); left: -1rem; display: grid; grid-template-columns: repeat(3, minmax(200px, 1fr)); gap: 1.5rem; padding: 1.4rem; background: var(--surface); color: var(--fg); border: 1px solid var(--border); border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); width: max-content; animation: drop 0.18s var(--ease);
		h3 { font-size: var(--fs-sm); margin-bottom: 0.5rem; }
		a { display: flex; align-items: center; gap: 0.65rem; padding: 0.5rem 0.55rem; color: var(--fg-muted); border-radius: var(--radius-sm); font-size: var(--fs-sm); &:hover { background: var(--surface-2); color: var(--fg); } }
		.i { width: 30px; height: 30px; display: grid; place-items: center; border-radius: 9px; background: var(--primary-soft); color: var(--primary); }
	}
	.right { display: flex; align-items: center; gap: 0.6rem; }
	.signin { color: #fff; font-weight: 700; font-size: var(--fs-sm); padding: 0.5rem 0.7rem; &:hover { text-decoration: none; color: var(--brand-cyan); } }
	.burger { display: none; width: 40px; height: 40px; place-items: center; border: 1.5px solid rgb(255 255 255 / 0.28); background: none; color: #fff; border-radius: var(--radius); }

	.drawer-scrim { position: fixed; inset: 0; z-index: var(--z-drawer); background: var(--scrim); }
	.drawer { position: fixed; inset: 0 0 0 auto; width: min(380px, 92vw); z-index: calc(var(--z-drawer) + 1); background: var(--brand-navy); color: #fff; display: flex; flex-direction: column; animation: slide 0.25s var(--ease);
		.d-head { display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.25rem; button { background: none; border: 0; color: #fff; display: grid; } }
		nav { flex: 1; overflow-y: auto; padding: 0.5rem 1.25rem; display: grid; align-content: start; a { color: #d3e2f6; padding: 0.7rem 0; font-weight: 700; border-bottom: 1px solid rgb(255 255 255 / 0.07); &.sub { font-weight: 500; font-size: var(--fs-sm); padding: 0.5rem 0 0.5rem 0.8rem; border: 0; } } h3 { margin: 1.2rem 0 0.2rem; font-size: var(--fs-xs); color: var(--brand-cyan); } }
		.d-foot { padding: 1.25rem; display: grid; gap: 0.75rem; border-top: 1px solid rgb(255 255 255 / 0.08); }
		:global(.on-dark) { color: #fff; border-color: rgb(255 255 255 / 0.3); }
	}
	@keyframes drop { from { opacity: 0; transform: translateY(-6px); } }
	@keyframes slide { from { transform: translateX(30px); opacity: 0; } }
	@media (max-width: 980px) { .links, .signin, .right :global(.cta) { display: none; } .burger { display: grid; } .bar { justify-content: space-between; } .right { gap: 0.4rem; } }
</style>
