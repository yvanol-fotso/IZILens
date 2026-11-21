<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { MODULES, moduleEnabled } from '$lib/config/modules';
	import type { SessionUser } from '$lib/types';
	import { Badge, Card } from '$lib/components/shared';

	let { user }: { user: SessionUser } = $props();
	const { t } = getI18n();
</script>

<Card title={t('dashboard.modules')}>
	<ul>
		{#each MODULES as m (m.id)}
			{@const Icon = m.icon}
			{@const on = moduleEnabled(user, m.id)}
			<li class:off={!on}>
				<span class="ico"><Icon size={18} /></span>
				<a href={m.href}><b>{t(`modules.${m.id}.title`)}</b><small>{t(`modules.${m.id}.desc`)}</small></a>
				{#if !on}<Badge>{t('modules.status.disabled')}</Badge>{:else if m.status === 'soon'}<Badge tone="info">{t('modules.status.soon')}</Badge>{:else}<Badge tone="success" dot>{t('modules.status.live')}</Badge>{/if}
			</li>
		{/each}
	</ul>
</Card>

<style lang="scss">
	ul { display: grid; gap: 0.2rem; margin: -0.3rem -0.5rem; }
	li { display: flex; align-items: center; gap: 0.8rem; padding: 0.6rem 0.5rem; border-radius: var(--radius-sm); &:hover { background: var(--surface-2); } &.off { opacity: 0.65; } }
	.ico { width: 36px; height: 36px; border-radius: 11px; display: grid; place-items: center; background: var(--primary-soft); color: var(--primary); flex-shrink: 0; }
	a { flex: 1; min-width: 0; display: grid; color: var(--fg); text-decoration: none !important; small { color: var(--fg-muted); font-size: var(--fs-xs); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; } }
</style>
