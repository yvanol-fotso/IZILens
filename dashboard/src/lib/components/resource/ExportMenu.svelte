<script lang="ts">
	import { Download } from '@lucide/svelte';
	import { page } from '$app/state';
	import { clickOutside } from '$lib/actions/clickOutside';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { exportHref, type ResourceDef } from '$lib/config/resources';
	import { Button } from '$lib/components/shared';

	let { def }: { def: ResourceDef } = $props();
	const { t } = getI18n();
	let open = $state(false);
	const qs = $derived(page.url.searchParams.toString());
</script>

<div class="exp" use:clickOutside={() => (open = false)}>
	<Button variant="outline" onclick={() => (open = !open)}>{#snippet icon()}<Download size={17} />{/snippet}{t('rx.ui.export')}</Button>
	{#if open}
		<div class="menu">{#each ['csv', 'xlsx', 'pdf'] as f (f)}<a href={exportHref(def, f as 'csv', qs)} download data-sveltekit-reload>{t(`rx.ui.export_${f}`)}</a>{/each}</div>
	{/if}
</div>

<style lang="scss">
	.exp { position: relative; } .menu { position: absolute; right: 0; top: calc(100% + 6px); z-index: 10; min-width: 170px; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow-lg); padding: 0.3rem; a { display: block; padding: 0.55rem 0.8rem; border-radius: var(--radius-sm); color: var(--fg); font-weight: 600; font-size: var(--fs-sm); &:hover { background: var(--surface-2); text-decoration: none; } } }
</style>
