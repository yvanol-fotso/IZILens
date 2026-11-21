<script lang="ts">
	import { ArrowLeft } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { can } from '$lib/config/permissions';
	import { moduleEnabled } from '$lib/config/modules';
	import { CaseSummary, DecisionPanel, DocumentViewer, ExtractedData } from '$lib/components/verifications';
	import { Button, PageHeader } from '$lib/components/shared';

	let { data, form } = $props();
	const { t } = getI18n();
	const kyc = $derived(data.kyc);
</script>

<PageHeader title={kyc.reference || kyc.id.slice(0, 8)} subtitle={kyc.id}>
	{#snippet actions()}<Button href="/app/verifications" variant="ghost">{#snippet icon()}<ArrowLeft size={18} />{/snippet}{t('common.back')}</Button>{/snippet}
</PageHeader>

<div class="layout">
	<div class="main stack">
		<CaseSummary {kyc} />
		<DocumentViewer caseId={kyc.id} documents={kyc.documents} />
		<ExtractedData {kyc} />
	</div>
	<aside>
		<DecisionPanel {form} canDecide={can(data.user.role, 'cases:decide')} pending={kyc.status === 'pending_review'} canLiveness={can(data.user.role, 'liveness:manage') && moduleEnabled(data.user, 'liveness')} />
	</aside>
</div>

<style lang="scss">
	.layout { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 1.25rem; align-items: start; }
	aside { position: sticky; top: 84px; }
	@media (max-width: 1000px) { .layout { grid-template-columns: 1fr; } aside { position: static; } }
</style>
