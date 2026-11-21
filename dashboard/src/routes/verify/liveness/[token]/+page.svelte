<script lang="ts">
	import { page } from '$app/state';
	import { MobileCapture } from '$lib/components/liveness';
</script>

<svelte:head><title>IZI LENS</title><meta name="robots" content="noindex" /></svelte:head>
<main id="main"><MobileCapture token={page.params.token ?? ''} /></main>
