<script lang="ts">
	import { LogOut, Menu, Settings, ChevronDown } from '@lucide/svelte';
	import { clickOutside } from '$lib/actions/clickOutside';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { sidebarOpen } from '$lib/stores/ui';
	import type { SessionUser } from '$lib/types';
	import { Avatar, LanguageSwitcher, ThemeToggle } from '$lib/components/shared';

	let { user }: { user: SessionUser } = $props();
	const { t } = getI18n();
	let open = $state(false);
</script>

<header class="top">
	<button type="button" class="menu" onclick={() => ($sidebarOpen = true)} aria-label={t('app.openMenu')}><Menu size={22} /></button>
	<div class="org">
		<strong>{user.organization?.name ?? 'Kafintech'}</strong>
		<span>{t(`roles.${user.role}`)}</span>
	</div>
	<div class="spacer"></div>
	<LanguageSwitcher />
	<ThemeToggle />
	<div class="user" use:clickOutside={() => (open = false)}>
		<button type="button" class="u-btn" onclick={() => (open = !open)} aria-expanded={open} aria-haspopup="menu">
			<Avatar name={user.full_name} size={34} />
			<span class="nm">{user.full_name}</span>
			<ChevronDown size={16} />
		</button>
		{#if open}
			<div class="pop" role="menu">
				<div class="who"><b>{user.full_name}</b><span>{user.email}</span></div>
				<a href="/app/settings" role="menuitem"><Settings size={16} />{t('app.nav.settings')}</a>
				<form method="POST" action="/api/auth/logout">
					<button type="submit" role="menuitem"><LogOut size={16} />{t('app.signOut')}</button>
				</form>
			</div>
		{/if}
	</div>
</header>

<style lang="scss">
	.top { position: sticky; top: 0; z-index: 20; height: 64px; display: flex; align-items: center; gap: 0.7rem; padding: 0 1.5rem; background: color-mix(in srgb, var(--bg) 88%, transparent); backdrop-filter: blur(10px); border-bottom: 1px solid var(--border); }
	.menu { display: none; width: 40px; height: 40px; place-items: center; border: 1.5px solid var(--border-strong); background: none; border-radius: var(--radius); color: var(--fg); }
	.org { display: grid; line-height: 1.2; strong { font-size: var(--fs-sm); } span { font-size: var(--fs-xs); color: var(--fg-muted); } }
	.user { position: relative; }
	.u-btn { display: flex; align-items: center; gap: 0.55rem; padding: 0.25rem 0.5rem 0.25rem 0.25rem; border-radius: var(--radius-pill); border: 1.5px solid var(--border-strong); background: var(--surface); color: var(--fg); &:hover { border-color: var(--primary); } }
	.nm { font-weight: 700; font-size: var(--fs-sm); max-width: 140px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.pop { position: absolute; right: 0; top: calc(100% + 8px); min-width: 240px; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow-lg); padding: 0.4rem; animation: drop 0.15s var(--ease);
		.who { display: grid; padding: 0.6rem 0.7rem 0.7rem; border-bottom: 1px solid var(--border); margin-bottom: 0.3rem; span { font-size: var(--fs-xs); color: var(--fg-muted); } }
		a, button { width: 100%; display: flex; align-items: center; gap: 0.6rem; padding: 0.6rem 0.7rem; border: 0; background: none; color: var(--fg); font-weight: 600; font-size: var(--fs-sm); border-radius: var(--radius-sm); text-align: left; &:hover { background: var(--surface-2); text-decoration: none; } } }
	@keyframes drop { from { opacity: 0; transform: translateY(-4px); } }
	@media (max-width: 1024px) { .menu { display: grid; } }
	@media (max-width: 560px) { .nm, .org span { display: none; } .top { padding: 0 1rem; } }
</style>
