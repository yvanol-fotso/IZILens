<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import Badge from './Badge.svelte';
	let { status }: { status: string } = $props();
	const { t } = getI18n();
	const tones: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'neutral'> = {
		approved: 'success', pending_review: 'warning', rejected: 'danger', processing: 'info', failed: 'neutral'
	};
</script>

<Badge tone={tones[status] ?? 'neutral'} dot>{t(`status.${status}`)}</Badge>
