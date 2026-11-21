<script lang="ts">
	import { enhance } from '$app/forms';
	import { Check, X, ScanFace } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { toastSuccess } from '$lib/stores/toast';
	import type { FormState } from '$lib/types';
	import { Button, Card, FormAlert } from '$lib/components/shared';

	let { form, canDecide, pending, canLiveness }: { form?: FormState | null; canDecide: boolean; pending: boolean; canLiveness: boolean } = $props();
	const { t } = getI18n();
	let loading = $state<'approved' | 'rejected' | null>(null);
	let reason = $state('');
</script>

<Card title={t('verifications.detail.decisionTitle')} description={t('verifications.detail.decisionHint')}>
	{#if !canDecide}
		<p class="muted">{t('errors.forbidden')}</p>
	{:else if !pending}
		<p class="muted">{t('verifications.detail.notPending')}</p>
	{:else}
		<form method="POST" action="?/decide" class="stack" use:enhance={({ submitter }) => { loading = (submitter as HTMLButtonElement | null)?.value as 'approved' | 'rejected'; return async ({ result, update }) => { if (result.type === 'success') toastSuccess(t('verifications.detail.decisionDone')); await update({ reset: false }); loading = null; }; }}>
			<FormAlert {form} />
			<label class="reason">
				<span>{t('verifications.detail.reason')}</span>
				<textarea name="reason" rows="3" bind:value={reason} placeholder={t('verifications.detail.reasonPlaceholder')} maxlength="1000"></textarea>
			</label>
			<div class="row">
				<Button type="submit" name="decision" value="approved" variant="brand" loading={loading === 'approved'} disabled={loading !== null}>{#snippet icon()}<Check size={18} />{/snippet}{t('verifications.detail.approve')}</Button>
				<Button type="submit" name="decision" value="rejected" variant="danger" loading={loading === 'rejected'} disabled={loading !== null}>{#snippet icon()}<X size={18} />{/snippet}{t('verifications.detail.reject')}</Button>
			</div>
		</form>
	{/if}
	{#if canLiveness}
		<hr />
		<Button href="/app/liveness" variant="outline" size="sm">{#snippet icon()}<ScanFace size={16} />{/snippet}{t('verifications.detail.triggerLiveness')}</Button>
	{/if}
</Card>

<style lang="scss">
	.reason { display: grid; gap: 0.4rem; font-size: var(--fs-sm); font-weight: 700; }
	textarea { width: 100%; resize: vertical; padding: 0.8rem 0.95rem; border: 1.5px solid var(--border-strong); border-radius: var(--radius); background: var(--surface); font-weight: 400; &:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 4px var(--ring); } }
	hr { border: 0; border-top: 1px solid var(--border); margin: 1.2rem 0; }
</style>
