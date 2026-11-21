<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { HTMLButtonAttributes } from 'svelte/elements';
	import Spinner from './Spinner.svelte';

	type Props = Omit<HTMLButtonAttributes, 'children'> & {
		variant?: 'primary' | 'brand' | 'outline' | 'ghost' | 'danger';
		size?: 'sm' | 'md' | 'lg';
		href?: string;
		loading?: boolean;
		block?: boolean;
		icon?: Snippet;
		iconAfter?: Snippet;
		children?: Snippet;
	};

	let { variant = 'primary', size = 'md', href, loading = false, block = false, icon, iconAfter, children, class: className = '', disabled, type = 'button', ...rest }: Props = $props();
	const anchorProps = $derived(rest as Record<string, unknown>);
</script>

{#if href && !disabled}
	<a {href} class="btn {variant} {size} {className}" class:block {...anchorProps}>
		{#if icon}{@render icon()}{/if}
		{@render children?.()}
		{#if iconAfter}{@render iconAfter()}{/if}
	</a>
{:else}
	<button {type} class="btn {variant} {size} {className}" class:block disabled={disabled || loading} aria-busy={loading} {...rest}>
		{#if loading}<Spinner size={16} />{:else if icon}{@render icon()}{/if}
		{@render children?.()}
		{#if iconAfter}{@render iconAfter()}{/if}
	</button>
{/if}

<style lang="scss">
	.btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 0.55rem;
		border: 1.5px solid transparent;
		border-radius: var(--radius);
		font-weight: 700;
		line-height: 1;
		white-space: nowrap;
		text-decoration: none !important;
		transition: background 0.18s var(--ease), border-color 0.18s var(--ease), transform 0.18s var(--ease), box-shadow 0.18s var(--ease);
		&:active:not(:disabled) { transform: translateY(1px); }
		&:disabled { opacity: 0.55; cursor: not-allowed; }
		&.block { width: 100%; }
		:global(svg) { flex-shrink: 0; }
	}
	.sm { padding: 0.55rem 0.85rem; font-size: var(--fs-sm); border-radius: var(--radius-sm); }
	.md { padding: 0.8rem 1.25rem; font-size: var(--fs-sm); }
	.lg { padding: 1.05rem 1.7rem; font-size: var(--fs-md); }

	.primary { background: var(--cta); color: var(--cta-fg); &:hover:not(:disabled) { background: var(--cta-hover); box-shadow: 0 8px 24px -10px var(--brand-cyan); } }
	.brand { background: var(--primary); color: var(--primary-fg); &:hover:not(:disabled) { background: var(--primary-hover); } }
	.outline { background: transparent; color: var(--fg); border-color: var(--border-strong); &:hover:not(:disabled) { border-color: var(--primary); color: var(--primary); } }
	.ghost { background: transparent; color: var(--fg-muted); &:hover:not(:disabled) { background: var(--surface-2); color: var(--fg); } }
	.danger { background: var(--danger-bg); color: var(--danger); border-color: transparent; &:hover:not(:disabled) { border-color: var(--danger); } }
</style>
