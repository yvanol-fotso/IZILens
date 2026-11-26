<script lang="ts">
	import type { Snippet } from 'svelte';
	let { title, kicker, children, actions, media }: { title: string; kicker?: string; children?: Snippet; actions?: Snippet; media?: Snippet } = $props();
</script>

<section class="hero">
	<div class="container" class:split={media}>
		<div class="copy">
			{#if kicker}<p class="kicker">{kicker}</p>{/if}
			<h1>{title}</h1>
			{#if children}<div class="txt">{@render children()}</div>{/if}
			{#if actions}<div class="acts">{@render actions()}</div>{/if}
		</div>
		{#if media}<div class="media">{@render media()}</div>{/if}
	</div>
</section>

<style lang="scss">
	.hero { background: var(--brand-navy); color: #fff; padding: calc(var(--header-h) + 4rem) 0 4.5rem; background-image: radial-gradient(60% 120% at 88% 0%, rgb(34 199 242 / 0.22), transparent 62%), radial-gradient(40% 80% at 0% 100%, rgb(0 143 203 / 0.28), transparent 70%); }
	.split { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr); gap: 3.5rem; align-items: center; }
	.media { --img-radius: var(--radius-xl, 28px); border-radius: var(--radius-xl, 28px); box-shadow: 0 40px 80px -30px rgb(0 0 0 / 0.6); border: 1px solid rgb(255 255 255 / 0.12); overflow: hidden; max-width: 480px; justify-self: end; width: 100%; }
	.kicker { color: var(--brand-cyan); font-weight: 700; font-style: italic; margin-bottom: 1rem; font-size: var(--fs-sm); }
	h1 { font-size: clamp(2rem, 1.3rem + 3vw, 3.6rem); max-width: 22ch; letter-spacing: -0.035em; }
	.txt { margin-top: 1.4rem; max-width: 62ch; color: #a9bfdc; font-size: var(--fs-lg); display: grid; gap: 0.9rem; line-height: 1.65; }
	.acts { margin-top: 2rem; display: flex; gap: 0.8rem; flex-wrap: wrap; :global(.ghost-light) { color: #fff; border-color: rgb(255 255 255 / 0.3); &:hover { border-color: var(--brand-cyan) !important; color: var(--brand-cyan) !important; } } }
	@media (max-width: 900px) { .split { grid-template-columns: 1fr; gap: 2.5rem; } .media { justify-self: start; max-width: 420px; } }
</style>
