<script lang="ts">
	import { CookiesDocument } from '$lib/components/cookies';
	let { data } = $props();
</script>

<CookiesDocument doc={data.doc} />
