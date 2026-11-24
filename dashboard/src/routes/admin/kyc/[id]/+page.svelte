<script lang="ts">
	import { ArrowLeft } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { can } from '$lib/config/permissions';
	import { ReviewPanel } from '$lib/components/admin';
	import { DataTable } from '$lib/components/resource';
	import { CaseSummary, DocumentViewer, ExtractedData } from '$lib/components/verifications';
	import { Button, Card, PageHeader } from '$lib/components/shared';
	let { data, form } = $props();
	const { t } = getI18n();
	const kyc = $derived(data.kyc);
</script>

<PageHeader title={kyc.reference || kyc.id.slice(0, 8)} subtitle="{kyc.client_name ?? ''} · {kyc.id}">
	{#snippet actions()}<Button href="/admin/kyc" variant="ghost">{#snippet icon()}<ArrowLeft size={18} />{/snippet}{t('common.back')}</Button>{/snippet}
</PageHeader>
<div class="layout">
	<div class="stack">
		<CaseSummary {kyc} />
		<DocumentViewer caseId={kyc.id} documents={kyc.documents} base="/api/admin/admin/kyc/cases" />
		<ExtractedData {kyc} />
		<Card title={t('rx.s.history')} padded={false}><DataTable cols={[{ key: 'created_at', type: 'datetime' }, { key: 'actor' }, { key: 'action', type: 'mono' }, { key: 'reason' }]} rows={data.history} /></Card>
	</div>
	<aside><ReviewPanel {form} canReview={can(data.user.role, 'adm:kyc:review')} pending={['pending_review', 'manual_review', 'pending'].includes(kyc.status)} /></aside>
</div>

<style lang="scss">
	.layout { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 1.25rem; align-items: start; } aside { position: sticky; top: 84px; } @media (max-width: 1000px) { .layout { grid-template-columns: 1fr; } aside { position: static; } }
</style>
