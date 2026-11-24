<script lang="ts">
	import { CircleCheck } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Button, CopyButton } from '$lib/components/shared';
	let { reference }: { reference: string } = $props();
	const { t } = getI18n();
</script>

<div class="ok" role="status">
	<CircleCheck size={56} />
	<h2>{t('contact.confirm.title')}</h2>
	<p>{t('contact.confirm.text')}</p>
	<div class="ref"><span>{t('contact.confirm.ref')}</span><code>{reference}</code><CopyButton text={reference} /></div>
	<Button href="/contact" variant="outline">{t('contact.confirm.another')}</Button>
</div>

<style lang="scss">
	.ok { display: grid; justify-items: center; text-align: center; gap: 1rem; padding: 3rem 1.5rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-xl); :global(svg:first-child) { color: var(--success); } h2 { font-size: var(--fs-2xl); } p { color: var(--fg-muted); max-width: 56ch; } }
	.ref { display: flex; flex-wrap: wrap; gap: 0.8rem; align-items: center; justify-content: center; padding: 0.8rem 1.2rem; background: var(--surface-2); border-radius: var(--radius); span { font-size: var(--fs-sm); color: var(--fg-muted); font-weight: 700; } code { font-size: var(--fs-lg); font-weight: 800; letter-spacing: 0.04em; } }
</style>
