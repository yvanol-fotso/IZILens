<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import Badge from './Badge.svelte';
	let { level }: { level: string | null | undefined } = $props();
	const { t } = getI18n();
	const tones: Record<string, 'success' | 'warning' | 'danger'> = { low: 'success', medium: 'warning', high: 'danger' };
</script>

<Badge tone={level ? tones[level] : 'neutral'}>{t(`risk.${level ?? 'none'}`)}</Badge>
