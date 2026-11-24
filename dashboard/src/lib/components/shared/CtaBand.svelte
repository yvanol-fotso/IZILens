<script lang="ts">
	import type { Snippet } from 'svelte';
	let { title, children, actions, id }: { title: string; children?: Snippet; actions?: Snippet; id?: string } = $props();
</script>

<section {id} class="cta">
	<div class="container">
		<h2>{title}</h2>
		{#if children}<div class="txt">{@render children()}</div>{/if}
		{#if actions}<div class="acts">{@render actions()}</div>{/if}
	</div>
</section>

<style lang="scss">
	.cta { background: var(--brand-navy); color: #fff; padding: 5rem 0; text-align: center; background-image: radial-gradient(50% 90% at 0% 100%, rgb(0 143 203 / 0.35), transparent 70%), radial-gradient(40% 70% at 100% 0%, rgb(34 199 242 / 0.2), transparent 70%); }
	h2 { font-size: var(--fs-3xl); max-width: 22ch; margin-inline: auto; }
	.txt { margin: 1.2rem auto 0; max-width: 62ch; color: #a9bfdc; display: grid; gap: 0.8rem; font-size: var(--fs-lg); }
	.acts { margin-top: 2rem; display: flex; gap: 0.8rem; justify-content: center; flex-wrap: wrap; :global(.ghost-light) { color: #fff; border-color: rgb(255 255 255 / 0.3); &:hover { border-color: var(--brand-cyan) !important; color: var(--brand-cyan) !important; } } }
</style>
