<script lang="ts">
	import { Plus, Trash2 } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import type { Field } from '$lib/config/resources';
	import { Button, Input, Select, Switch, Textarea } from '$lib/components/shared';
	import Self from './FieldInputs.svelte';
	import { fieldLabel, optLabel } from './labels';

	type Row = Record<string, any>;
	let { fields, init = {}, errors = {}, namer = (n: string) => n, staff = [] }: { fields: Field[]; init?: Row; errors?: Record<string, string>; namer?: (n: string) => string; staff?: { id: string; full_name: string }[] } = $props();
	const { t } = getI18n();
	let rows = $state<Record<string, number[]>>({});
	const counters: Record<string, number> = {};
	const add = (name: string) => { counters[name] = (counters[name] ?? 0) + 1; rows[name] = [...(rows[name] ?? []), counters[name]]; };
	const err = (name: string) => (errors[namer(name)] ? t(errors[namer(name)]) : undefined);
	const lbl = (f: Field) => `${fieldLabel(t, f.name)}${f.required ? ' *' : ''}`;
	const val = (f: Field) => String(init[f.from ?? f.name] ?? '');
</script>

<div class="fields">
	{#each fields as f (f.name)}
		{#if f.type === 'textarea'}
			<Textarea label={lbl(f)} name={namer(f.name)} value={val(f)} hint={f.hint} error={err(f.name)} maxlength={4000} />
		{:else if f.type === 'select'}
			<Select label={lbl(f)} name={namer(f.name)} value={val(f) || (f.required ? (f.options?.[0] ?? '') : '')} hint={f.hint} error={err(f.name)} options={[...(f.required ? [] : [{ value: '', label: t('rx.ui.none') }]), ...(f.options ?? []).map((o) => ({ value: o, label: optLabel(t, o) }))]} />
		{:else if f.type === 'staff'}
			<Select label={lbl(f)} name={namer(f.name)} value={val(f)} error={err(f.name)} options={[{ value: '', label: t('rx.ui.none') }, ...staff.map((s) => ({ value: s.id, label: s.full_name }))]} />
		{:else if f.type === 'multiselect'}
			<fieldset><legend>{lbl(f)}</legend>
				<div class="chk">{#each f.options ?? [] as o (o)}<label><input type="checkbox" name={namer(f.name)} value={o} checked={Array.isArray(init[f.name]) && init[f.name].includes(o)} />{optLabel(t, o)}</label>{/each}</div>
				{#if err(f.name)}<p class="err">{err(f.name)}</p>{/if}
			</fieldset>
		{:else if f.type === 'switch'}
			<Switch name={namer(f.name)} label={fieldLabel(t, f.name)} description={f.hint} checked={!!init[f.name]} />
		{:else if f.type === 'file'}
			<div class="file"><label for={namer(f.name)}>{lbl(f)}</label><input id={namer(f.name)} type="file" name={namer(f.name)} accept={f.accept} multiple={f.multiple} />{#if err(f.name)}<p class="err">{err(f.name)}</p>{/if}</div>
		{:else if f.type === 'repeater'}
			<fieldset class="rep"><legend>{fieldLabel(t, f.name)}</legend>
				{#each rows[f.name] ?? [] as n, i (n)}
					<div class="row-box">
						<Self fields={f.fields ?? []} namer={(x) => `${namer(f.name)}[${n}][${x}]`} {errors} {staff} />
						<button type="button" class="rm" aria-label={t('rx.ui.removeRow')} onclick={() => (rows[f.name] = rows[f.name].filter((x) => x !== n))}><Trash2 size={16} /></button>
					</div>
				{/each}
				<Button variant="outline" size="sm" onclick={() => add(f.name)}>{#snippet icon()}<Plus size={16} />{/snippet}{t('rx.ui.addRow')}</Button>
			</fieldset>
		{:else}
			<Input label={lbl(f)} name={namer(f.name)} type={f.type === 'text' ? 'text' : f.type} value={f.secret ? '' : val(f)} hint={f.hint} error={err(f.name)} min={f.min} max={f.max} autocomplete="off" placeholder={f.secret && init[f.name] ? '••••••••' : undefined} />
		{/if}
	{/each}
</div>

<style lang="scss">
	.fields { display: grid; gap: 1rem; }
	fieldset { border: 0; padding: 0; margin: 0; display: grid; gap: 0.6rem; } legend { font-size: var(--fs-sm); font-weight: 700; margin-bottom: 0.5rem; }
	.chk { display: flex; flex-wrap: wrap; gap: 0.5rem; label { display: flex; align-items: center; gap: 0.45rem; padding: 0.45rem 0.8rem; border: 1.5px solid var(--border-strong); border-radius: var(--radius-pill); font-size: var(--fs-sm); font-weight: 600; cursor: pointer; &:has(input:checked) { background: var(--primary-soft); border-color: var(--primary); } input { accent-color: var(--primary); } } }
	.file { display: grid; gap: 0.4rem; label { font-size: var(--fs-sm); font-weight: 700; } input { padding: 0.6rem; border: 1.5px dashed var(--border-strong); border-radius: var(--radius); background: var(--surface-2); } }
	.rep { padding: 1rem; border: 1px dashed var(--border-strong); border-radius: var(--radius); } .row-box { position: relative; padding: 1rem 2.6rem 1rem 1rem; background: var(--surface-2); border-radius: var(--radius); .rm { position: absolute; top: 0.6rem; right: 0.6rem; border: 0; background: none; color: var(--danger); display: grid; } }
	.err { color: var(--danger); font-size: var(--fs-xs); font-weight: 600; }
</style>
