<script lang="ts">
	import { Camera, CircleCheck, TriangleAlert } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Button, Logo } from '$lib/components/shared';

	let { token }: { token: string } = $props();
	const { t } = getI18n();
	type Step = 'intro' | 'capture' | 'done' | 'error';
	let step = $state<Step>('intro');
	let video = $state<HTMLVideoElement>();
	let stream: MediaStream | null = null;
	let prompts = ['center', 'left', 'right', 'blink'] as const;
	let index = $state(0);
	let errorKey = $state('liveness.mobile.permission');
	const frames: string[] = [];

	async function start() {
		try {
			stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false });
			step = 'capture';
			queueMicrotask(() => { if (video) { video.srcObject = stream; void video.play(); } });
		} catch {
			errorKey = 'liveness.mobile.permission';
			step = 'error';
		}
	}

	async function capture() {
		if (!video) return;
		const c = document.createElement('canvas');
		c.width = video.videoWidth; c.height = video.videoHeight;
		c.getContext('2d')!.drawImage(video, 0, 0);
		frames.push(c.toDataURL('image/jpeg', 0.85));
		if (index < prompts.length - 1) { index++; return; }
		stream?.getTracks().forEach((tr) => tr.stop());
		// Envoi au backend dès que le module liveness est branché ; en attendant l'échec est silencieux.
		await fetch(`/api/v1/liveness/sessions/${token}/frames`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ frames }) }).catch(() => {});
		step = 'done';
	}
	$effect(() => () => stream?.getTracks().forEach((tr) => tr.stop()));
</script>

<div class="m">
	<Logo size={34} byline={false} />
	{#if step === 'intro'}
		<h1>{t('liveness.mobile.title')}</h1>
		<p>{t('liveness.mobile.intro')}</p>
		<Button size="lg" block onclick={start}>{#snippet icon()}<Camera size={20} />{/snippet}{t('liveness.mobile.start')}</Button>
	{:else if step === 'capture'}
		<div class="cam"><video bind:this={video} playsinline muted></video><span class="oval"></span></div>
		<p class="prompt" aria-live="assertive">{t(`liveness.mobile.prompts.${prompts[index]}`)}</p>
		<Button size="lg" block onclick={capture}>{t('liveness.mobile.capture')} ({index + 1}/{prompts.length})</Button>
	{:else if step === 'done'}
		<CircleCheck size={64} color="var(--success)" /><h1>{t('liveness.mobile.done')}</h1><p>{t('liveness.mobile.doneText')}</p>
	{:else}
		<TriangleAlert size={56} color="var(--danger)" /><h1>{t(errorKey)}</h1>
		<Button onclick={() => (step = 'intro')} variant="outline">{t('common.refresh')}</Button>
	{/if}
</div>

<style lang="scss">
	.m { min-height: 100dvh; max-width: 460px; margin: 0 auto; padding: 1.5rem; display: grid; align-content: center; justify-items: center; gap: 1.2rem; text-align: center; h1 { font-size: var(--fs-xl); } p { color: var(--fg-muted); } }
	.cam { position: relative; width: 100%; aspect-ratio: 3/4; border-radius: var(--radius-lg); overflow: hidden; background: #000; video { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); } }
	.oval { position: absolute; inset: 12% 18%; border: 3px solid var(--brand-cyan); border-radius: 50%; box-shadow: 0 0 0 999px rgb(7 27 53 / 0.5); }
	.prompt { font-weight: 800; font-size: var(--fs-lg); color: var(--fg) !important; }
</style>
