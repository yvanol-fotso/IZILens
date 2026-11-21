<script lang="ts">
	import { TermsDocument } from '$lib/components/terms';
	let { data } = $props();
</script>

<TermsDocument doc={data.doc} />
