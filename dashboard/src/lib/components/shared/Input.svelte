<script lang="ts">
	import type { Component } from 'svelte';
	import { Eye, EyeOff } from '@lucide/svelte';
	import type { HTMLInputAttributes } from 'svelte/elements';

	type Props = Omit<HTMLInputAttributes, 'value'> & {
		label: string;
		value?: string;
		error?: string;
		hint?: string;
		icon?: Component<any>;
	};
	let { label, value = $bindable(''), error, hint, icon: Icon, type = 'text', id, class: className = '', ...rest }: Props = $props();

	const uid = $props.id();
	const fieldId = $derived(id ?? `f-${uid}`);
	let reveal = $state(false);
	const isPassword = $derived(type === 'password');
</script>

<div class="field {className}" class:invalid={!!error}>
	<label for={fieldId}>{label}</label>
	<div class="control">
		{#if Icon}<span class="lead"><Icon size={18} /></span>{/if}
		<input
			id={fieldId}
			type={isPassword && reveal ? 'text' : type}
			bind:value
			aria-invalid={!!error}
			aria-describedby={error || hint ? `${fieldId}-msg` : undefined}
			class:has-icon={!!Icon}
			{...rest}
		/>
		{#if isPassword}
			<button type="button" class="toggle" onclick={() => (reveal = !reveal)} aria-label={reveal ? 'Hide' : 'Show'}>
				{#if reveal}<EyeOff size={18} />{:else}<Eye size={18} />{/if}
			</button>
		{/if}
	</div>
	{#if error}<p id="{fieldId}-msg" class="msg err">{error}</p>{:else if hint}<p id="{fieldId}-msg" class="msg">{hint}</p>{/if}
</div>

<style lang="scss">
	.field { display: grid; gap: 0.4rem; }
	label { font-size: var(--fs-sm); font-weight: 700; }
	.control { position: relative; display: flex; align-items: center; }
	input {
		width: 100%;
		padding: 0.8rem 0.95rem;
		border: 1.5px solid var(--border-strong);
		border-radius: var(--radius);
		background: var(--surface);
		transition: border-color 0.15s, box-shadow 0.15s;
		&.has-icon { padding-left: 2.6rem; }
		&::placeholder { color: var(--fg-subtle); }
		&:hover { border-color: var(--fg-subtle); }
		&:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 4px var(--ring); }
	}
	.invalid input { border-color: var(--danger); }
	.lead { position: absolute; left: 0.85rem; color: var(--fg-subtle); display: grid; }
	.toggle { position: absolute; right: 0.4rem; border: 0; background: none; color: var(--fg-subtle); padding: 0.45rem; border-radius: var(--radius-sm); display: grid; &:hover { color: var(--fg); } }
	.msg { font-size: var(--fs-xs); color: var(--fg-muted); }
	.err { color: var(--danger); font-weight: 600; }
</style>
