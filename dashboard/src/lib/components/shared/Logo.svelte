<script lang="ts">
	let { size = 36, text = true, tone = 'auto', byline = true, href = '/' }: { size?: number; text?: boolean; tone?: 'auto' | 'light'; byline?: boolean; href?: string | null } = $props();
</script>

<svelte:element this={href ? 'a' : 'span'} {href} class="logo" class:light={tone === 'light'} aria-label="IZI LENS">
	<svg width={size} height={size} viewBox="0 0 48 48" aria-hidden="true">
		<rect width="48" height="48" rx="13" class="bg" />
		<path d="M12 19v-4a3 3 0 0 1 3-3h4M36 19v-4a3 3 0 0 0-3-3h-4M12 29v4a3 3 0 0 0 3 3h4M36 29v4a3 3 0 0 1-3 3h-4" class="brackets" />
		<circle cx="24" cy="24" r="6" class="eye" />
		<circle cx="24" cy="24" r="1.8" class="pupil" />
	</svg>
	{#if text}
		<span class="words">
			<span class="name">IZI <b>LENS</b></span>
			{#if byline}<span class="by">by Kafintech Group</span>{/if}
		</span>
	{/if}
</svelte:element>

<style lang="scss">
	.logo {
		display: inline-flex;
		align-items: center;
		gap: 0.65rem;
		color: var(--fg);
		text-decoration: none !important;
		&.light { color: #fff; }
	}
	.bg { fill: var(--brand-navy); }
	.brackets { fill: none; stroke: var(--brand-cyan); stroke-width: 3; stroke-linecap: round; }
	.eye { fill: none; stroke: #fff; stroke-width: 3; }
	.pupil { fill: var(--brand-cyan); }
	.words { display: grid; line-height: 1; gap: 3px; }
	.name { font-weight: 800; font-size: 1.15rem; letter-spacing: -0.02em; b { color: var(--primary); font-weight: 800; } }
	.light .name b { color: var(--brand-cyan); }
	.by { font-size: 0.62rem; font-weight: 600; opacity: 0.7; letter-spacing: 0.02em; }
</style>
