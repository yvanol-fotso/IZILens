<script lang="ts">
	import { Moon, Sun } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { applyTheme, currentTheme } from '$lib/utils/theme';

	let { variant = 'default' }: { variant?: 'default' | 'light' } = $props();
	const { t } = getI18n();
	let dark = $state(false);
	$effect(() => {
		dark = currentTheme() === 'dark';
	});
	function toggle() {
		dark = !dark;
		applyTheme(dark ? 'dark' : 'light');
	}
</script>

<button type="button" class="tt {variant}" onclick={toggle} aria-label={t('nav.theme')} title={t('nav.theme')}>
	{#if dark}<Sun size={18} />{:else}<Moon size={18} />{/if}
</button>

<style lang="scss">
	.tt { width: 40px; height: 40px; display: grid; place-items: center; border-radius: var(--radius); border: 1.5px solid var(--border-strong); background: transparent; color: var(--fg); &:hover { border-color: var(--primary); } &.light { color: #fff; border-color: rgb(255 255 255 / 0.28); &:hover { border-color: var(--brand-cyan); } } }
</style>
