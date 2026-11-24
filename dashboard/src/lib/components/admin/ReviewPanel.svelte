<script lang="ts">
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import { Check, X, RotateCcw } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { toastSuccess } from '$lib/stores/toast';
	import type { FormState } from '$lib/types';
	import { Button, Card, FormAlert, Textarea } from '$lib/components/shared';

	/** Revue manuelle KYC par un agent Kafintech : motif obligatoire + éléments justificatifs. */
	let { form = null, canReview, pending }: { form?: FormState | null; canReview: boolean; pending: boolean } = $props();
	const { t } = getI18n();
	let loading = $state<string | null>(null);
</script>

<Card title={t('verifications.detail.decisionTitle')} description={t('verifications.detail.decisionHint')}>
	{#if !canReview}<p class="muted">{t('errors.forbidden')}</p>
	{:else if !pending}<p class="muted">{t('verifications.detail.notPending')}</p>
	{:else}
		<form method="POST" action="?/decide" class="stack" use:enhance={({ submitter }) => { loading = (submitter as HTMLButtonElement | null)?.value ?? null; return async ({ result, update }) => { if (result.type === 'success') { toastSuccess(t('verifications.detail.decisionDone')); await invalidateAll(); } await update({ reset: false }); loading = null; }; }}>
			<FormAlert {form} />
			<Textarea label="{t('verifications.detail.reason')} *" name="reason" placeholder={t('verifications.detail.reasonPlaceholder')} maxlength={1000} />
			<Textarea label={t('rx.f.evidence')} name="evidence" maxlength={2000} />
			<div class="row">
				<Button type="submit" name="decision" value="approved" variant="brand" loading={loading === 'approved'} disabled={!!loading}>{#snippet icon()}<Check size={18} />{/snippet}{t('verifications.detail.approve')}</Button>
				<Button type="submit" name="decision" value="rejected" variant="danger" loading={loading === 'rejected'} disabled={!!loading}>{#snippet icon()}<X size={18} />{/snippet}{t('verifications.detail.reject')}</Button>
				<Button type="submit" name="decision" value="request_new" variant="outline" loading={loading === 'request_new'} disabled={!!loading}>{#snippet icon()}<RotateCcw size={16} />{/snippet}{t('rx.a.request_new')}</Button>
			</div>
		</form>
	{/if}
</Card>
