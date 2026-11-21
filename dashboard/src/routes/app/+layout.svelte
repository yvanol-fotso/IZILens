<script lang="ts">
	import type { Snippet } from 'svelte';
	import { Sidebar, Topbar } from '$lib/components/layout';
	import { getI18n } from '$lib/i18n/index.svelte';

	let { data, children }: { data: { user: import('$lib/types').SessionUser }; children: Snippet } = $props();
	const { t } = getI18n();
</script>

<svelte:head><title>{t('meta.app')} · IZI LENS</title><meta name="robots" content="noindex" /></svelte:head>

<div class="app">
	<Sidebar user={data.user} />
	<div class="col">
		<Topbar user={data.user} />
		<main id="main">{@render children()}</main>
	</div>
</div>

<style lang="scss">
	.app { display: flex; min-height: 100dvh; }
	.col { flex: 1; min-width: 0; display: flex; flex-direction: column; }
	main { padding: 2rem clamp(1rem, 3vw, 2.5rem) 4rem; width: min(100%, 1280px); margin-inline: auto; flex: 1; }
</style>
