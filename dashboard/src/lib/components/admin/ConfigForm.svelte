<script lang="ts">
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import { getI18n } from '$lib/i18n/index.svelte';
	import type { ConfigPage } from '$lib/config/admin-config';
	import { toastSuccess } from '$lib/stores/toast';
	import type { FormState } from '$lib/types';
	import { Button, Card, FormAlert, Input, Textarea } from '$lib/components/shared';
	import { FieldInputs, UnavailableNotice, sectionLabel } from '$lib/components/resource';

	let { page, values, unavailable, form = null, readonly = false }: { page: ConfigPage; values: Record<string, any>; unavailable: boolean; form?: FormState | null; readonly?: boolean } = $props();
	const { t } = getI18n();
	let loading = $state(false);
	const err = (k: string) => (form?.errors?.[k] ? t(form.errors[k]) : undefined);
	// Les listes (IP, e-mails) arrivent en tableau : on les affiche une par ligne.
	const init = $derived(Object.fromEntries(Object.entries(values).map(([k, v]) => [k, Array.isArray(v) && !['languages', 'currencies', 'mfa_methods', 'aml_lists'].includes(k) ? v.join('\n') : v])));
</script>

{#if unavailable}
	<Card padded={false}><UnavailableNotice endpoint={page.endpoint} /></Card>
{:else}
	<form method="POST" action="?/save" class="stack" use:enhance={() => { loading = true; return async ({ result, update }) => { if (result.type === 'success') { toastSuccess(t('rx.ui.done')); await invalidateAll(); } await update({ reset: false }); loading = false; }; }}>
		<FormAlert {form} />
		{#each page.sections as s (s.key)}
			<Card title={sectionLabel(t, s.key)}>
				<fieldset disabled={readonly}>
					<FieldInputs fields={s.fields} {init} errors={form?.errors ?? {}} />
					{#each s.fields.filter((f) => f.secret) as f (f.name)}{#if values[`${f.name}_set`]}<p class="set">✓ {t('rx.ui.secretSet')}</p>{/if}{/each}
				</fieldset>
			</Card>
		{/each}
		{#if !readonly}
			<Card title={t('rx.ui.confirmChange')}>
				<div class="stack">
					<Textarea label="{t('rx.ui.reason')} *" name="reason" error={err('reason')} hint={t('rx.ui.reasonHint')} />
					{#if page.critical}<Input label="{t('rx.ui.stepUp')} *" name="step_up_code" inputmode="numeric" maxlength={6} autocomplete="one-time-code" hint={t('rx.ui.stepUpHint')} error={err('step_up_code')} />{/if}
					<div><Button type="submit" variant="brand" {loading}>{t('common.save')}</Button></div>
				</div>
			</Card>
		{/if}
	</form>
{/if}

<style lang="scss">
	fieldset { border: 0; padding: 0; margin: 0; display: grid; gap: 0.8rem; } .set { color: var(--success); font-size: var(--fs-xs); font-weight: 700; }
</style>
