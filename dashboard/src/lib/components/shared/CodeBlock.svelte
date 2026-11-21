<script lang="ts">
	import CopyButton from './CopyButton.svelte';
	let { code, language = 'bash' }: { code: string; language?: string } = $props();
</script>

<div class="code">
	<div class="bar"><span>{language}</span><CopyButton text={code} /></div>
	<pre><code>{code}</code></pre>
</div>

<style lang="scss">
	.code { border-radius: var(--radius); background: var(--brand-navy); color: #d6e6fb; overflow: hidden; border: 1px solid var(--brand-navy-3); }
	.bar { display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0.75rem 0.5rem 1rem; background: var(--brand-navy-2); font-size: var(--fs-xs); color: #8aa4c4; font-family: var(--font-mono); :global(.cp) { background: transparent; color: #cfe3fb; border-color: var(--brand-navy-3); } }
	pre { margin: 0; padding: 1rem 1.1rem; overflow-x: auto; font-size: 0.82rem; line-height: 1.65; }
</style>
