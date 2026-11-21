<script lang="ts">
	import type { Snippet } from 'svelte';
	import { X } from '@lucide/svelte';

	let { open = $bindable(false), title, description, size = 'md', children, footer, dismissible = true }: { open?: boolean; title: string; description?: string; size?: 'sm' | 'md' | 'lg'; children?: Snippet; footer?: Snippet; dismissible?: boolean } = $props();
	let dialog = $state<HTMLDialogElement>();

	$effect(() => {
		if (!dialog) return;
		if (open && !dialog.open) dialog.showModal();
		if (!open && dialog.open) dialog.close();
	});
</script>

<dialog bind:this={dialog} class={size} onclose={() => (open = false)} oncancel={(e) => !dismissible && e.preventDefault()} onclick={(e) => dismissible && e.target === dialog && (open = false)}>
	<div class="panel">
		<header>
			<div>
				<h2>{title}</h2>
				{#if description}<p>{description}</p>{/if}
			</div>
			{#if dismissible}<button type="button" class="x" onclick={() => (open = false)} aria-label="Close"><X size={20} /></button>{/if}
		</header>
		<div class="content">{@render children?.()}</div>
		{#if footer}<footer>{@render footer()}</footer>{/if}
	</div>
</dialog>

<style lang="scss">
	dialog { border: 0; padding: 0; background: transparent; max-width: 100vw; width: 100%; margin: auto; color: var(--fg); &::backdrop { background: var(--scrim); backdrop-filter: blur(3px); } }
	dialog[open] .panel { animation: pop 0.22s var(--ease); }
	.sm .panel { max-width: 420px; } .md .panel { max-width: 540px; } .lg .panel { max-width: 760px; }
	.panel { margin: 0 auto; width: calc(100% - 2rem); background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); }
	header { display: flex; justify-content: space-between; gap: 1rem; padding: 1.35rem 1.5rem 0; }
	h2 { font-size: var(--fs-xl); }
	p { color: var(--fg-muted); font-size: var(--fs-sm); margin-top: 0.3rem; }
	.x { border: 0; background: none; color: var(--fg-muted); height: 36px; width: 36px; display: grid; place-items: center; border-radius: var(--radius-sm); flex-shrink: 0; &:hover { background: var(--surface-2); } }
	.content { padding: 1.25rem 1.5rem; }
	footer { display: flex; justify-content: flex-end; gap: 0.6rem; padding: 0 1.5rem 1.4rem; flex-wrap: wrap; }
	@keyframes pop { from { opacity: 0; transform: translateY(10px) scale(0.98); } }
</style>
