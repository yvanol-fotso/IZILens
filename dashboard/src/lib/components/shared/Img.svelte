<script module lang="ts">
	/** Ordre d'essai des extensions (la première qui existe dans /static gagne). */
	export const IMG_EXTS = ['svg', 'webp', 'avif', 'png', 'jpg', 'jpeg', 'gif'];
	const EXT_RE = /\.(svg|webp|avif|png|jpe?g|gif)$/i;
	/** Mémoire : évite de re-tester les extensions déjà résolues. */
	const resolved = new Map<string, string>();
</script>

<script lang="ts">
	import { ImageOff } from '@lucide/svelte';

	interface Props {
		/** Chemin SANS extension (ex: "/marketing/home/hero"). Une extension reste acceptée. */
		src: string;
		alt?: string;
		exts?: string[];
		/** ex: "16/9", "4/3" */
		ratio?: string;
		fit?: 'cover' | 'contain';
		loading?: 'lazy' | 'eager';
		width?: number;
		height?: number;
	}

	let { src, alt = '', exts = IMG_EXTS, ratio, fit = 'cover', loading = 'lazy', width, height }: Props = $props();

	const base = $derived(src.replace(EXT_RE, ''));
	const candidates = $derived.by(() => {
		const list = [...(EXT_RE.test(src) ? [src] : []), ...exts.map((e) => `${base}.${e}`)];
		const hit = resolved.get(base);
		return [...new Set(hit ? [hit, ...list] : list)];
	});

	// Index de l'extension en cours d'essai, par image.
	let tried = $state<Record<string, number>>({});
	const index = $derived(tried[base] ?? 0);
	const current = $derived(candidates[index]);

	function onerror() {
		tried[base] = index + 1; // essaie l'extension suivante ; au bout → placeholder
	}
	function onload() {
		resolved.set(base, current);
	}
</script>

<div class="img" style:aspect-ratio={ratio}>
	{#if current}
		<img src={current} {alt} {width} {height} {loading} decoding="async" style:object-fit={fit} {onload} {onerror} />
	{:else}
		<div class="ph" role="img" aria-label={alt || 'Image indisponible'}><ImageOff size={32} /></div>
	{/if}
</div>

<style lang="scss">
	.img { position: relative; width: 100%; overflow: hidden; border-radius: var(--img-radius, var(--radius-lg)); background: var(--bg-soft); }
	img { display: block; width: 100%; height: 100%; }
	.ph { position: absolute; inset: 0; display: grid; place-items: center; color: var(--fg-muted); background: repeating-linear-gradient(135deg, var(--bg-soft) 0 12px, var(--surface) 12px 24px); }
</style>