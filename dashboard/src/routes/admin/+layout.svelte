<script lang="ts">
	import type { Snippet } from 'svelte';
	import { Sidebar, Topbar } from '$lib/components/layout';
	import { adminNav, visibleGroups } from '$lib/config/navigation';
	import { getI18n } from '$lib/i18n/index.svelte';
	import type { SessionUser } from '$lib/types';

	let { data, children }: { data: { user: SessionUser }; children: Snippet } = $props();
	const { t } = getI18n();
	const groups = $derived(visibleGroups(adminNav, data.user));
</script>

<svelte:head><title>Kafintech · IZI LENS</title><meta name="robots" content="noindex, nofollow" /></svelte:head>

<div class="app">
	<Sidebar {groups} home="/admin" admin footer={t(`roles.${data.user.role}`)} />
	<div class="col"><Topbar user={data.user} /><main id="main">{@render children()}</main></div>
</div>

<style lang="scss">
	.app { display: flex; min-height: 100dvh; } .col { flex: 1; min-width: 0; display: flex; flex-direction: column; }
	main { padding: 2rem clamp(1rem, 3vw, 2.5rem) 4rem; width: min(100%, 1400px); margin-inline: auto; flex: 1; }
</style>
