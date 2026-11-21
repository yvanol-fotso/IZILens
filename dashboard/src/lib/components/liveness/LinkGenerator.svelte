<script lang="ts">
	import QRCode from 'qrcode';
	import { Link2, QrCode } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Button, Card, CopyButton, Input, Badge } from '$lib/components/shared';

	const { t } = getI18n();
	let reference = $state('');
	let loading = $state(false);
	let link = $state('');
	let qr = $state('');
	let demo = $state(false);
	let error = $state('');
	let minutes = $state(15);

	async function generate() {
		loading = true;
		error = '';
		try {
			let token: string;
			// Le module backend n'existe pas encore : on essaie, sinon on passe en démonstration.
			const res = await fetch('/api/v1/liveness/sessions', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ case_reference: reference || undefined }) });
			if (res.ok) {
				const body = await res.json();
				token = body.token ?? body.session_token ?? body.id;
				minutes = body.expires_in_minutes ?? 15;
				demo = false;
			} else {
				token = crypto.randomUUID().replaceAll('-', '');
				demo = true;
			}
			link = `${location.origin}/verify/liveness/${token}`;
			qr = await QRCode.toDataURL(link, { margin: 1, width: 240, color: { dark: '#101e2d', light: '#ffffff' } });
		} catch {
			error = t('liveness.generate.error');
		} finally {
			loading = false;
		}
	}
</script>

<Card title={t('liveness.generate.title')}>
	<div class="grid">
		<div class="stack">
			<Input label="{t('liveness.generate.caseRef')}" name="ref" bind:value={reference} maxlength={64} />
			<Button onclick={generate} {loading}>{#snippet icon()}<QrCode size={18} />{/snippet}{t('liveness.generate.button')}</Button>
			{#if error}<p class="err">{error}</p>{/if}
			{#if link}
				<div class="link">
					<span class="lbl"><Link2 size={15} />{t('liveness.generate.linkLabel')}</span>
					<code>{link}</code>
					<div class="row"><CopyButton text={link} /><small>{t('liveness.generate.expires', { minutes })}</small></div>
					{#if demo}<Badge tone="warning">{t('liveness.generate.demo')}</Badge>{/if}
				</div>
			{/if}
		</div>
		<div class="qr" aria-live="polite">
			{#if qr}<img src={qr} alt="QR code" width="240" height="240" /><p>{t('liveness.generate.scan')}</p>{:else}<span class="ph"><QrCode size={56} /></span>{/if}
		</div>
	</div>
</Card>

<style lang="scss">
	.grid { display: grid; grid-template-columns: 1fr 260px; gap: 2rem; align-items: start; }
	.link { display: grid; gap: 0.6rem; padding: 1rem; border: 1px solid var(--border); border-radius: var(--radius); background: var(--surface-2); code { word-break: break-all; font-size: var(--fs-xs); } small { color: var(--fg-muted); } .lbl { display: flex; align-items: center; gap: 0.4rem; font-size: var(--fs-xs); font-weight: 700; color: var(--fg-muted); } }
	.qr { display: grid; justify-items: center; gap: 0.6rem; text-align: center; img { border-radius: var(--radius); border: 1px solid var(--border); } p { font-size: var(--fs-sm); color: var(--fg-muted); } }
	.ph { width: 240px; height: 240px; display: grid; place-items: center; border: 2px dashed var(--border-strong); border-radius: var(--radius); color: var(--fg-subtle); }
	.err { color: var(--danger); font-size: var(--fs-sm); font-weight: 600; }
	@media (max-width: 800px) { .grid { grid-template-columns: 1fr; } }
</style>
