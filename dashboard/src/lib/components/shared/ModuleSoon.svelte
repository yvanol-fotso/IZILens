<script lang="ts">
	import type { Component, Snippet } from 'svelte';
	import { Check, Hammer } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import Badge from './Badge.svelte';
	import PageHeader from './PageHeader.svelte';

	/** Page « module en préparation » : l'interface est réservée, le backend se branche plus tard. */
	let { title, subtitle, features, icon: Icon, children }: { title: string; subtitle: string; features: string[]; icon: Component<any>; children?: Snippet } = $props();
	const { t } = getI18n();
</script>

<PageHeader {title} {subtitle} />

<div class="soon">
	<div class="art" aria-hidden="true">
		<span class="ring r1"></span><span class="ring r2"></span>
		<span class="core"><Icon size={34} /></span>
	</div>
	<div class="copy">
		<Badge tone="brand"><Hammer size={13} />{t('modules.soon.badge')}</Badge>
		<p>{t('modules.soon.desc')}</p>
		<ul>
			{#each features as f (f)}<li><Check size={16} />{f}</li>{/each}
		</ul>
		{@render children?.()}
	</div>
</div>

<style lang="scss">
	.soon { display: grid; grid-template-columns: 280px 1fr; gap: 2.5rem; align-items: center; background: var(--surface); border: 1px dashed var(--border-strong); border-radius: var(--radius-xl); padding: 2.5rem; }
	.art { position: relative; aspect-ratio: 1; display: grid; place-items: center; }
	.ring { position: absolute; border-radius: 50%; border: 1.5px solid var(--border-strong); inset: 0; &.r2 { inset: 16%; border-color: var(--brand-cyan); animation: pulse 3s ease-in-out infinite; } }
	.core { width: 84px; height: 84px; border-radius: 26px; display: grid; place-items: center; background: var(--brand-navy); color: var(--brand-cyan); box-shadow: var(--shadow-lg); }
	.copy { display: grid; gap: 1rem; justify-items: start; p { color: var(--fg-muted); max-width: 52ch; } }
	ul { display: grid; gap: 0.6rem; li { display: flex; gap: 0.6rem; align-items: center; font-weight: 600; :global(svg) { color: var(--success); } } }
	@keyframes pulse { 50% { transform: scale(1.06); opacity: 0.5; } }
	@media (max-width: 760px) { .soon { grid-template-columns: 1fr; padding: 1.5rem; } .art { max-width: 200px; } }
</style>
