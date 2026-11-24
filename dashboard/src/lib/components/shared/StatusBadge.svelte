<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import Badge from './Badge.svelte';
	let { status }: { status: string } = $props();
	const { t } = getI18n();
	const tones: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'neutral'> = {
		verified: 'success', manual_review: 'warning', not_verified: 'danger', processing: 'info', in_progress: 'info',
		action_required: 'warning', created: 'neutral', failed: 'danger', expired: 'neutral'
	};
</script>

<Badge tone={tones[status] ?? 'neutral'} dot>{t(`status.${status}`)}</Badge>
