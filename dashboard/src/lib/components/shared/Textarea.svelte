<script lang="ts">
	import type { HTMLTextareaAttributes } from 'svelte/elements';
	type Props = Omit<HTMLTextareaAttributes, 'value'> & { label: string; value?: string; error?: string; hint?: string };
	let { label, value = $bindable(''), error, hint, id, ...rest }: Props = $props();
	const uid = $props.id();
	const fid = $derived(id ?? `t-${uid}`);
</script>

<div class="field" class:invalid={!!error}>
	<label for={fid}>{label}</label>
	<textarea id={fid} bind:value aria-invalid={!!error} rows="5" {...rest}></textarea>
	{#if error}<p class="msg err">{error}</p>{:else if hint}<p class="msg">{hint}</p>{/if}
</div>

<style lang="scss">
	.field { display: grid; gap: 0.4rem; } label { font-size: var(--fs-sm); font-weight: 700; }
	textarea { width: 100%; resize: vertical; padding: 0.8rem 0.95rem; border: 1.5px solid var(--border-strong); border-radius: var(--radius); background: var(--surface); &:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 4px var(--ring); } }
	.invalid textarea { border-color: var(--danger); } .msg { font-size: var(--fs-xs); color: var(--fg-muted); } .err { color: var(--danger); font-weight: 600; }
</style>
