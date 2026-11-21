<script lang="ts">
	import type { Snippet } from 'svelte';
	import { Footer, Navbar } from '$lib/components/layout';
	let { children }: { children: Snippet } = $props();
</script>

<div class="site">
	<Navbar />
	<main id="main">{@render children()}</main>
	<Footer />
</div>

<style>
	.site { min-height: 100dvh; display: flex; flex-direction: column; }
	main { flex: 1; }
</style>
