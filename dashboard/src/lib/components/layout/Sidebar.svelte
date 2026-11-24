<script lang="ts">
	import { X } from '@lucide/svelte';
	import { page } from '$app/state';
	import { focusTrap } from '$lib/actions/focusTrap';
	import { adminNav, appNav, type NavItem } from '$lib/config/navigation';
	import { moduleEnabled } from '$lib/config/modules';
	import { can } from '$lib/config/permissions';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { sidebarOpen } from '$lib/stores/ui';
	import type { SessionUser } from '$lib/types';
	import { Badge, Logo } from '$lib/components/shared';

	let { user }: { user: SessionUser } = $props();
	const { t } = getI18n();
	const path = $derived(page.url.pathname);

	const visible = (item: NavItem) => (!item.permission || can(user.role, item.permission)) && (!item.module || moduleEnabled(user, item.module));
	const groups = $derived(appNav.map((g) => ({ ...g, items: g.items.filter(visible) })).filter((g) => g.items.length));
	const isActive = (item: NavItem) => (item.exact ? path === item.href : path === item.href || path.startsWith(item.href + '/'));

	$effect(() => {
		void path;
		$sidebarOpen = false;
	});
</script>

{#snippet link(item: NavItem)}
	{@const Icon = item.icon}
	<a href={item.href} class:active={isActive(item)} aria-current={isActive(item) ? 'page' : undefined}>
		<Icon size={19} />
		<span>{t(`app.nav.${item.key}`)}</span>
		{#if item.soon}<Badge tone="neutral">{t('app.soonBadge')}</Badge>{/if}
	</a>
{/snippet}

{#snippet content()}
	<div class="head"><Logo tone="light" size={36} byline={false} href="/app" /></div>
	<nav aria-label="App">
		{#each groups as g (g.key)}
			<div class="group">
				<h3>{t(`app.groups.${g.key}`)}</h3>
				{#each g.items as item (item.href)}{@render link(item)}{/each}
			</div>
		{/each}
		{#if user.role === 'super_admin'}
			<div class="group admin">
				<h3>{t('app.groups.admin')}</h3>
				{#each adminNav as item (item.href)}{@render link(item)}{/each}
			</div>
		{/if}
	</nav>
	<div class="org">
		<span>{user.organization?.name ?? 'Kafintech'}</span>
	</div>
{/snippet}

<aside class="side">{@render content()}</aside>

{#if $sidebarOpen}
	<div class="scrim" role="presentation" onclick={() => ($sidebarOpen = false)}></div>
	<aside class="side drawer" use:focusTrap>
		<button type="button" class="close" onclick={() => ($sidebarOpen = false)} aria-label={t('common.close')}><X size={20} /></button>
		{@render content()}
	</aside>
{/if}

<style lang="scss">
	.side { position: sticky; top: 0; height: 100dvh; width: var(--sidebar-w); flex-shrink: 0; background: var(--brand-navy); color: #c2d3ea; display: flex; flex-direction: column; border-right: 1px solid rgb(255 255 255 / 0.06); }
	.head { padding: 1.25rem 1.3rem 1rem; }
	nav { flex: 1; overflow-y: auto; padding: 0.25rem 0.8rem 1rem; display: grid; gap: 1.1rem; align-content: start; }
	.group { display: grid; gap: 0.15rem; }
	h3 { font-size: 0.72rem; font-weight: 700; color: #6f89ab; padding: 0 0.7rem; margin-bottom: 0.3rem; }
	a { display: flex; align-items: center; gap: 0.7rem; padding: 0.62rem 0.75rem; border-radius: var(--radius-sm); font-size: var(--fs-sm); font-weight: 600; color: #c2d3ea; span { flex: 1; } :global(.badge) { background: rgb(255 255 255 / 0.1); color: #9db4d1; font-size: 0.66rem; padding: 0.1rem 0.45rem; }
		&:hover { background: rgb(255 255 255 / 0.07); color: #fff; text-decoration: none; }
		&.active { background: linear-gradient(90deg, rgb(34 199 242 / 0.2), rgb(34 199 242 / 0.04)); color: #fff; box-shadow: inset 3px 0 0 var(--brand-cyan); :global(svg) { color: var(--brand-cyan); } } }
	.admin { padding-top: 0.9rem; border-top: 1px dashed rgb(255 255 255 / 0.12); h3 { color: var(--accent-orange); } }
	.org { padding: 0.9rem 1.3rem; border-top: 1px solid rgb(255 255 255 / 0.07); font-size: var(--fs-xs); font-weight: 700; color: #8aa4c4; }
	.scrim { position: fixed; inset: 0; background: var(--scrim); z-index: var(--z-drawer); }
	.drawer { position: fixed; inset: 0 auto 0 0; z-index: calc(var(--z-drawer) + 1); animation: slide 0.25s var(--ease); }
	.close { position: absolute; top: 1rem; right: 0.8rem; background: none; border: 0; color: #fff; display: grid; z-index: 1; }
	@keyframes slide { from { transform: translateX(-30px); opacity: 0; } }
	@media (max-width: 1024px) { .side:not(.drawer) { display: none; } }
</style>
