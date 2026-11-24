<script lang="ts">
	import { ChevronDown, Menu, X, ArrowRight } from '@lucide/svelte';
	import { page } from '$app/state';
	import { clickOutside } from '$lib/actions/clickOutside';
	import { focusTrap } from '$lib/actions/focusTrap';
	import { marketingNav } from '$lib/config/navigation';
	import { SERVICES, demoHref } from '$lib/config/services';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { mobileNavOpen } from '$lib/stores/ui';
	import { Button, LanguageSwitcher, Logo, ThemeToggle } from '$lib/components/shared';

	const { t } = getI18n();
	let open = $state(false);
	let scrolled = $state(false);
	const user = $derived(page.data.user);
	const path = $derived(page.url.pathname);
	const links = marketingNav.filter((l) => l.enabled);
	const active = (href: string) => path === href || path.startsWith(href + '/');

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
		open = false;
	});
</script>

<header class="nav" class:scrolled>
	<div class="container bar">
		<Logo tone="light" size={38} />

		<nav class="links" aria-label="Main">
			<div class="dd" use:clickOutside={() => (open = false)}>
				<button type="button" class="dd-btn" class:act={active('/services')} aria-expanded={open} onclick={() => (open = !open)}>{t('nav.services')}<ChevronDown size={16} /></button>
				{#if open}
					<div class="mega">
						{#each SERVICES as s (s.id)}
							{@const Icon = s.icon}
							<a href="/services/{s.slug}"><span class="i" style:--c={s.color}><Icon size={18} /></span><span class="tx"><b>{t(`svc.items.${s.id}.code`)}</b><small>{t(`svc.items.${s.id}.name`)}</small></span></a>
						{/each}
						<a class="all" href="/services">{t('footer.links.services')} <ArrowRight size={15} /></a>
					</div>
				{/if}
			</div>
			{#each links as l (l.key)}<a href={l.href} aria-current={active(l.href) ? 'page' : undefined} class:act={active(l.href)}>{t(`nav.${l.key}`)}</a>{/each}
		</nav>

		<div class="right">
			<LanguageSwitcher variant="light" />
			<ThemeToggle variant="light" />
			{#if user}
				<Button href="/app" size="sm" class="cta">{t('nav.openApp')}</Button>
			{:else}
				<a class="signin" href="/login">{t('nav.signIn')}</a>
				<Button href={demoHref} size="sm" class="cta">{t('nav.demo')}</Button>
			{/if}
			<button type="button" class="burger" onclick={() => ($mobileNavOpen = true)} aria-label={t('nav.menu')} aria-expanded={$mobileNavOpen} aria-controls="mobile-nav"><Menu size={22} /></button>
		</div>
	</div>
</header>

{#if $mobileNavOpen}
	<div class="drawer-scrim" role="presentation" onclick={() => ($mobileNavOpen = false)}></div>
	<div id="mobile-nav" class="drawer" role="dialog" aria-modal="true" use:focusTrap aria-label={t('nav.menu')}>
		<div class="d-head"><Logo tone="light" size={34} /><button type="button" onclick={() => ($mobileNavOpen = false)} aria-label={t('common.close')}><X size={22} /></button></div>
		<nav>
			<a href="/services">{t('nav.services')}</a>
			{#each SERVICES as s (s.id)}<a class="sub" href="/services/{s.slug}">{t(`svc.items.${s.id}.code`)}</a>{/each}
			{#each links as l (l.key)}<a href={l.href}>{t(`nav.${l.key}`)}</a>{/each}
		</nav>
		<div class="d-foot">
			<div class="row"><LanguageSwitcher variant="light" placement="up" /><ThemeToggle variant="light" /></div>
			{#if user}<Button href="/app" block>{t('nav.openApp')}</Button>{:else}
				<Button href="/login" variant="outline" block class="on-dark">{t('nav.signIn')}</Button>
				<Button href={demoHref} block>{t('nav.demo')}</Button>
			{/if}
		</div>
	</div>
{/if}

<style lang="scss">
	.nav { position: fixed; inset: 0 0 auto 0; z-index: var(--z-nav); height: var(--header-h); color: #fff; transition: background 0.25s, box-shadow 0.25s; &.scrolled { background: rgb(7 27 53 / 0.88); backdrop-filter: blur(14px) saturate(1.4); box-shadow: 0 1px 0 rgb(255 255 255 / 0.07); } }
	.bar { height: 100%; display: flex; align-items: center; gap: 2rem; }
	.links { display: flex; align-items: center; gap: 0.2rem; flex: 1; a, .dd-btn { color: #d3e2f6; font-weight: 600; font-size: var(--fs-sm); padding: 0.55rem 0.8rem; border-radius: var(--radius-sm); background: none; border: 0; display: inline-flex; align-items: center; gap: 0.3rem; &:hover, &.act { color: #fff; background: rgb(255 255 255 / 0.08); text-decoration: none; } &.act { box-shadow: inset 0 -2px 0 var(--brand-cyan); } } }
	.dd { position: relative; }
	.mega { position: absolute; top: calc(100% + 12px); left: 0; display: grid; gap: 0.2rem; padding: 0.6rem; width: 320px; background: var(--surface); color: var(--fg); border: 1px solid var(--border); border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); animation: drop 0.18s var(--ease);
		a { display: flex; align-items: center; gap: 0.75rem; padding: 0.6rem 0.7rem; color: var(--fg); border-radius: var(--radius-sm); &:hover { background: var(--surface-2); } }
		.i { width: 36px; height: 36px; display: grid; place-items: center; border-radius: 10px; background: color-mix(in srgb, var(--c) 15%, var(--surface)); color: var(--c); }
		.tx { display: grid; line-height: 1.25; small { color: var(--fg-muted); font-size: var(--fs-xs); } }
		.all { justify-content: space-between; border-top: 1px solid var(--border); border-radius: 0 0 var(--radius-sm) var(--radius-sm); margin-top: 0.3rem; font-size: var(--fs-sm); font-weight: 700; color: var(--primary); } }
	.right { display: flex; align-items: center; gap: 0.6rem; }
	.signin { color: #fff; font-weight: 700; font-size: var(--fs-sm); padding: 0.5rem 0.7rem; &:hover { text-decoration: none; color: var(--brand-cyan); } }
	.burger { display: none; width: 40px; height: 40px; place-items: center; border: 1.5px solid rgb(255 255 255 / 0.28); background: none; color: #fff; border-radius: var(--radius); }
	.drawer-scrim { position: fixed; inset: 0; z-index: var(--z-drawer); background: var(--scrim); }
	.drawer { position: fixed; inset: 0 0 0 auto; width: min(380px, 92vw); z-index: calc(var(--z-drawer) + 1); background: var(--brand-navy); color: #fff; display: flex; flex-direction: column; animation: slide 0.25s var(--ease);
		.d-head { display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.25rem; button { background: none; border: 0; color: #fff; display: grid; } }
		nav { flex: 1; overflow-y: auto; padding: 0.5rem 1.25rem; display: grid; align-content: start; a { color: #d3e2f6; padding: 0.8rem 0; font-weight: 700; border-bottom: 1px solid rgb(255 255 255 / 0.07); &.sub { font-weight: 500; font-size: var(--fs-sm); padding: 0.5rem 0 0.5rem 0.9rem; border: 0; } } }
		.d-foot { padding: 1.25rem; display: grid; gap: 0.75rem; border-top: 1px solid rgb(255 255 255 / 0.08); }
		:global(.on-dark) { color: #fff; border-color: rgb(255 255 255 / 0.3); } }
	@keyframes drop { from { opacity: 0; transform: translateY(-6px); } }
	@keyframes slide { from { transform: translateX(30px); opacity: 0; } }
	@media (max-width: 1040px) { .links, .signin, .right :global(.cta) { display: none; } .burger { display: grid; } .bar { justify-content: space-between; } .right { gap: 0.4rem; } }
</style>
