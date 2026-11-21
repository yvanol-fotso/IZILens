<script lang="ts">
	import { initials } from '$lib/utils/format';
	let { name, size = 36 }: { name: string; size?: number } = $props();
</script>

<span class="av" style:width="{size}px" style:height="{size}px" style:font-size="{size * 0.38}px" aria-hidden="true">{initials(name)}</span>

<style lang="scss">
	.av { display: inline-grid; place-items: center; border-radius: 50%; background: linear-gradient(135deg, var(--brand-blue), var(--accent-purple)); color: #fff; font-weight: 800; flex-shrink: 0; }
</style>
