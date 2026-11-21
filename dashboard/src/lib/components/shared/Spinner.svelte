<script lang="ts">
	let { size = 20 }: { size?: number } = $props();
</script>

<span class="spin" style:width="{size}px" style:height="{size}px" role="status" aria-label="Loading"></span>

<style lang="scss">
	.spin {
		display: inline-block;
		border-radius: 50%;
		border: 2px solid currentColor;
		border-right-color: transparent;
		animation: rot 0.7s linear infinite;
	}
	@keyframes rot { to { transform: rotate(360deg); } }
</style>
