<script lang="ts">
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { can } from '$lib/config/permissions';
	import type { Action, ResourceDef } from '$lib/config/resources';
	import { toastError, toastSuccess } from '$lib/stores/toast';
	import type { Role } from '$lib/types';
	import { Button, Input, Modal, Textarea } from '$lib/components/shared';
	import FieldInputs from './FieldInputs.svelte';
	import { actionLabel } from './labels';

	let { def, row, role, staff = [], compact = false }: { def: ResourceDef; row: Record<string, any>; role: Role; staff?: { id: string; full_name: string }[]; compact?: boolean } = $props();
	const { t } = getI18n();
	const visible = $derived((def.actions ?? []).filter((a) => can(role, a.permission) && (!a.when || a.when.in.includes(String(row[a.when.key])))));
	let current = $state<Action | null>(null);
	let open = $state(false);
	let loading = $state(false);
	let errors = $state<Record<string, string>>({});
	let message = $state('');
	const hasFile = $derived(!!current?.fields?.some((f) => f.type === 'file' || f.type === 'repeater'));
	const pick = (a: Action) => { current = a; errors = {}; message = ''; open = true; };
	$effect(() => { if (!open) current = null; });
</script>

{#if visible.length}
	<div class="acts" class:compact>
		{#each visible as a (a.id)}
			<Button size="sm" variant={a.tone === 'danger' ? 'danger' : a.tone === 'brand' ? 'brand' : 'outline'} onclick={() => pick(a)}>{actionLabel(t, a.id)}</Button>
		{/each}
	</div>
{/if}

{#if current}
	<Modal bind:open title={actionLabel(t, current.id)} description={current.critical ? t('rx.ui.criticalHint') : undefined}>
		<form id="act-{row.id}" method="POST" action="?/run" class="stack" enctype={hasFile ? 'multipart/form-data' : undefined}
			use:enhance={() => { loading = true; return async ({ result, update }) => {
				if (result.type === 'success') { toastSuccess(t('rx.ui.done')); open = false; await invalidateAll(); }
				else if (result.type === 'failure') { errors = (result.data?.errors as Record<string, string>) ?? {}; message = String(result.data?.message ?? ''); if (message) toastError(message); }
				else await update();
				loading = false; }; }}>
			<input type="hidden" name="__action" value={current.id} />
			<input type="hidden" name="__id" value={row.id} />
			{#if current.fields?.length}<FieldInputs fields={current.fields} {errors} {staff} />{/if}
			{#if current.reason}<Textarea label="{t('rx.ui.reason')} *" name="reason" error={errors.reason ? t(errors.reason) : undefined} hint={t('rx.ui.reasonHint')} maxlength={1000} />{/if}
			{#if current.critical}<Input label="{t('rx.ui.stepUp')} *" name="step_up_code" inputmode="numeric" pattern="[0-9]{6}" maxlength={6} autocomplete="one-time-code" hint={t('rx.ui.stepUpHint')} error={errors.step_up_code ? t(errors.step_up_code) : undefined} />{/if}
			{#if message}<p class="err">{message}</p>{/if}
		</form>
		{#snippet footer()}
			<Button variant="ghost" onclick={() => (open = false)}>{t('common.cancel')}</Button>
			<Button type="submit" form="act-{row.id}" variant={current?.tone === 'danger' ? 'danger' : 'brand'} {loading}>{t('common.confirm')}</Button>
		{/snippet}
	</Modal>
{/if}

<style lang="scss">
	.acts { display: flex; flex-wrap: wrap; gap: 0.5rem; &.compact { gap: 0.3rem; } } .err { color: var(--danger); font-size: var(--fs-sm); font-weight: 600; }
</style>
