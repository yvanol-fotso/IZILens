<script lang="ts">
	import { Cookie } from '@lucide/svelte';
	import { LegalDocument, Button } from '$lib/components/shared';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { openConsentCentre } from '$lib/stores/consent';
	import type { LegalDoc } from '$lib/server/markdown';

	let { doc }: { doc: LegalDoc } = $props();
	const { t } = getI18n();
</script>

<LegalDocument {doc}>
	{#snippet extra()}
		<Button variant="brand" onclick={openConsentCentre}>
			{#snippet icon()}<Cookie size={18} />{/snippet}
			{t('legal.manageCookies')}
		</Button>
	{/snippet}
</LegalDocument>
