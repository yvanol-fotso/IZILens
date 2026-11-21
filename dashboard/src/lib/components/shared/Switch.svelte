<script lang="ts">
	let { checked = $bindable(false), label, description, disabled = false, name, onchange }: { checked?: boolean; label: string; description?: string; disabled?: boolean; name?: string; onchange?: (v: boolean) => void } = $props();
</script>

<label class="sw" class:disabled>
	<span class="text">
		<span class="label">{label}</span>
		{#if description}<span class="desc">{description}</span>{/if}
	</span>
	<input type="checkbox" role="switch" {name} bind:checked {disabled} onchange={() => onchange?.(checked)} />
	<span class="track" aria-hidden="true"><span class="thumb"></span></span>
</label>

<style lang="scss">
	.sw { display: flex; align-items: center; justify-content: space-between; gap: 1rem; cursor: pointer; &.disabled { opacity: 0.6; cursor: not-allowed; } }
	.text { display: grid; gap: 2px; }
	.label { font-weight: 700; font-size: var(--fs-sm); }
	.desc { font-size: var(--fs-xs); color: var(--fg-muted); }
	input { position: absolute; opacity: 0; pointer-events: none; }
	.track { width: 44px; height: 26px; flex-shrink: 0; border-radius: var(--radius-pill); background: var(--surface-3); position: relative; transition: background 0.2s; }
	.thumb { position: absolute; top: 3px; left: 3px; width: 20px; height: 20px; border-radius: 50%; background: #fff; box-shadow: var(--shadow-sm); transition: transform 0.2s var(--ease); }
	input:checked + .track { background: var(--primary); .thumb { transform: translateX(18px); } }
	input:focus-visible + .track { outline: 3px solid var(--ring); outline-offset: 2px; }
</style>
