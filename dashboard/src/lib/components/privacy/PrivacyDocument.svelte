<script lang="ts">
	import { LegalDocument } from '$lib/components/shared';
	import type { LegalDoc } from '$lib/server/markdown';
	let { doc }: { doc: LegalDoc } = $props();
</script>

<LegalDocument {doc} />
