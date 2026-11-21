<script lang="ts">
	import { ChevronDown } from '@lucide/svelte';
	import type { HTMLSelectAttributes } from 'svelte/elements';

	type Props = Omit<HTMLSelectAttributes, 'value'> & {
		label?: string;
		value?: string;
		options: { value: string; label: string }[];
		hint?: string;
		error?: string;
	};
	let { label, value = $bindable(''), options, hint, error, id, class: className = '', ...rest }: Props = $props();
	const uid = $props.id();
	const fieldId = $derived(id ?? `s-${uid}`);
</script>

<div class="field {className}">
	{#if label}<label for={fieldId}>{label}</label>{/if}
	<div class="control">
		<select id={fieldId} bind:value aria-invalid={!!error} {...rest}>
			{#each options as o (o.value)}<option value={o.value}>{o.label}</option>{/each}
		</select>
		<span class="chev"><ChevronDown size={16} /></span>
	</div>
	{#if error}<p class="msg err">{error}</p>{:else if hint}<p class="msg">{hint}</p>{/if}
</div>

<style lang="scss">
	.field { display: grid; gap: 0.4rem; }
	label { font-size: var(--fs-sm); font-weight: 700; }
	.control { position: relative; }
	select {
		width: 100%; appearance: none; padding: 0.8rem 2.4rem 0.8rem 0.95rem;
		border: 1.5px solid var(--border-strong); border-radius: var(--radius); background: var(--surface);
		&:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 4px var(--ring); }
	}
	.chev { position: absolute; right: 0.85rem; top: 50%; transform: translateY(-50%); pointer-events: none; color: var(--fg-subtle); display: grid; }
	.msg { font-size: var(--fs-xs); color: var(--fg-muted); }
	.err { color: var(--danger); font-weight: 600; }
</style>
