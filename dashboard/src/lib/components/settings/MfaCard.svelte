<script lang="ts">
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import QRCode from 'qrcode';
	import { Fingerprint, ShieldCheck, Trash2 } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { toastError, toastSuccess } from '$lib/stores/toast';
	import type { FormState, SessionUser } from '$lib/types';
	import { Badge, Button, Card, CopyButton, FormAlert, Input } from '$lib/components/shared';
	import { formatDate } from '$lib/utils/format';

	let { user, form = null, passkeys = [] }: { user: SessionUser; form?: FormState | null; passkeys?: { id: string; name?: string; created_at?: string }[] } = $props();
	const i18n = getI18n();
	const { t } = i18n;
	const mine = $derived(form?.form === 'mfa' ? form : null);
	let qr = $state('');
	$effect(() => {
		const uri = (mine?.setup as { otpauth_uri?: string } | undefined)?.otpauth_uri;
		if (uri) QRCode.toDataURL(uri, { margin: 1, width: 200 }).then((d) => (qr = d));
	});
	const b64 = {
		dec: (s: string) => Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/').padEnd(Math.ceil(s.length / 4) * 4, '=')), (c) => c.charCodeAt(0)).buffer,
		enc: (b: ArrayBuffer) => btoa(String.fromCharCode(...new Uint8Array(b))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
	};

	/** Enregistrement d'une passkey (WebAuthn) : options → navigateur → vérification backend. */
	async function addPasskey() {
		try {
			const res = await fetch('/api/auth/passkeys/options', { method: 'POST' });
			if (!res.ok) throw new Error((await res.json()).detail);
			const o = await res.json();
			const cred = (await navigator.credentials.create({ publicKey: { ...o, challenge: b64.dec(o.challenge), user: { ...o.user, id: b64.dec(o.user.id) }, excludeCredentials: (o.excludeCredentials ?? []).map((c: any) => ({ ...c, id: b64.dec(c.id) })) } })) as PublicKeyCredential | null;
			if (!cred) return;
			const r = cred.response as AuthenticatorAttestationResponse;
			const verify = await fetch('/api/auth/passkeys/verify', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ id: cred.id, rawId: b64.enc(cred.rawId), type: cred.type, response: { clientDataJSON: b64.enc(r.clientDataJSON), attestationObject: b64.enc(r.attestationObject) } }) });
			if (!verify.ok) throw new Error((await verify.json()).detail);
			toastSuccess(t('rx.ui.done'));
			await invalidateAll();
		} catch (e) {
			toastError(e instanceof Error && e.message ? e.message : t('toast.error'));
		}
	}
</script>

<Card title={t('cli.mfa.title')} description={t('cli.mfa.subtitle')}>
	<div class="stack">
		<FormAlert form={mine} />
		<div class="row"><ShieldCheck size={20} /><b>TOTP</b><Badge tone={user.mfa_enabled ? 'success' : 'warning'} dot>{user.mfa_enabled ? t('common.active') : t('common.inactive')}</Badge></div>

		{#if mine?.recovery && (mine.recovery as string[]).length}
			<div class="rec"><b>{t('cli.mfa.recovery')}</b><p>{t('cli.mfa.recoveryHint')}</p><code>{(mine.recovery as string[]).join('  ')}</code><CopyButton text={(mine.recovery as string[]).join('\n')} /></div>
		{:else if mine?.setup}
			<div class="setup">
				{#if qr}<img src={qr} alt="QR code TOTP" width="200" height="200" />{/if}
				<div class="stack">
					<p>{t('cli.mfa.scan')}</p>
					<code class="secret">{(mine.setup as { secret?: string }).secret}</code>
					<form method="POST" action="?/totpConfirm" class="stack" use:enhance={() => async ({ update }) => { await update({ reset: false }); await invalidateAll(); }}>
						<Input label={t('auth.mfa.code')} name="code" inputmode="numeric" maxlength={6} autocomplete="one-time-code" error={mine?.errors?.code ? t(mine.errors.code) : undefined} />
						<div><Button type="submit" variant="brand">{t('common.confirm')}</Button></div>
					</form>
				</div>
			</div>
		{:else if !user.mfa_enabled}
			<form method="POST" action="?/totpSetup" use:enhance={() => async ({ update }) => update({ reset: false })}><Button type="submit" variant="brand">{t('cli.mfa.enable')}</Button></form>
		{:else}
			<form method="POST" action="?/mfaDisable" class="row" use:enhance={() => async ({ update }) => { await update({ reset: true }); await invalidateAll(); }}>
				<Input label={t('auth.mfa.code')} name="code" inputmode="numeric" maxlength={6} /><Button type="submit" variant="danger">{t('cli.mfa.disable')}</Button>
			</form>
		{/if}

		<hr />
		<div class="row"><Fingerprint size={20} /><b>Passkeys</b></div>
		{#each passkeys as p (p.id)}
			<div class="pk"><span>{p.name ?? 'Passkey'} <small>{formatDate(p.created_at, i18n.locale)}</small></span>
				<form method="POST" action="?/passkeyDelete" use:enhance={() => async ({ update }) => { await update({ reset: false }); await invalidateAll(); }}><input type="hidden" name="id" value={p.id} /><Button type="submit" size="sm" variant="danger" aria-label={t('common.delete')}>{#snippet icon()}<Trash2 size={15} />{/snippet}</Button></form></div>
		{/each}
		<div><Button variant="outline" onclick={addPasskey}>{t('cli.mfa.addPasskey')}</Button></div>
	</div>
</Card>

<style lang="scss">
	hr { border: 0; border-top: 1px solid var(--border); margin: 0.4rem 0; } .setup { display: grid; grid-template-columns: 200px 1fr; gap: 1.5rem; align-items: start; } .secret { padding: 0.5rem 0.8rem; background: var(--surface-2); border-radius: var(--radius-sm); word-break: break-all; font-size: var(--fs-xs); }
	.rec { padding: 1rem; border: 2px dashed var(--warning); border-radius: var(--radius); display: grid; gap: 0.6rem; background: var(--warning-bg); code { word-break: break-word; font-size: var(--fs-sm); } p { font-size: var(--fs-sm); } }
	.pk { display: flex; justify-content: space-between; align-items: center; padding: 0.6rem 0.9rem; background: var(--surface-2); border-radius: var(--radius-sm); small { color: var(--fg-muted); margin-left: 0.5rem; } }
	@media (max-width: 640px) { .setup { grid-template-columns: 1fr; } }
</style>
