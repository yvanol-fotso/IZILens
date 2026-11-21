<script lang="ts">
	import { TriangleAlert } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Button, CopyButton, Modal } from '$lib/components/shared';

	let { created = $bindable<{ name: string; key: string } | null>(null) }: { created?: { name: string; key: string } | null } = $props();
	const { t } = getI18n();
	let open = $state(false);
	$effect(() => { open = !!created; });
	$effect(() => { if (!open) created = null; });
</script>

<Modal bind:open title={t('apiKeys.created')} description={created?.name} dismissible={false}>
	<div class="warn"><TriangleAlert size={18} />{t('apiKeys.showOnce')}</div>
	<code>{created?.key}</code>
	{#snippet footer()}
		{#if created}<CopyButton text={created.key} size="md" />{/if}
		<Button variant="brand" onclick={() => (open = false)}>{t('common.close')}</Button>
	{/snippet}
</Modal>

<style lang="scss">
	.warn { display: flex; gap: 0.6rem; align-items: flex-start; padding: 0.8rem 1rem; border-radius: var(--radius); background: var(--warning-bg); color: var(--warning); font-size: var(--fs-sm); font-weight: 600; margin-bottom: 1rem; }
	code { display: block; padding: 1rem; background: var(--brand-navy); color: var(--brand-cyan); border-radius: var(--radius); word-break: break-all; font-size: 0.85rem; user-select: all; }
</style>
