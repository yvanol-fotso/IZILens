<script lang="ts">
	let {
		size = 36,
		href = '/',
		tone = 'auto',
		plate = false,
		variant = 'bicolor',
		// conservés pour compatibilité avec les anciens appels (ignorés : le PNG contient déjà le texte)
		text = true,
		byline = true
	}: {
		size?: number;
		href?: string | null;
		tone?: 'auto' | 'light';
		/** Fond blanc arrondi derrière le logo (utile si le logo est sombre sur fond navy). */
		plate?: boolean;
		/** 'bicolor' = logo secondaire (défaut), 'principal' = logo principal. */
		variant?: 'bicolor' | 'principal';
		text?: boolean;
		byline?: boolean;
	} = $props();

	const FILES = { bicolor: '/Bicolor.png', principal: '/Principal.png' } as const;
	let failed = $state(false);
	// Si Bicolor.png est introuvable, on retombe sur Principal.png.
	const src = $derived(failed ? FILES.principal : FILES[variant]);
</script>

<svelte:element this={href ? 'a' : 'span'} {href} class="logo" class:plate aria-label="IZI LENS">
	<img {src} alt="IZI LENS" style:height="{size}px" decoding="async" onerror={() => (failed = true)} />
</svelte:element>

<style lang="scss">
	.logo {
		display: inline-flex;
		align-items: center;
		text-decoration: none !important;
		&.plate { background: #fff; padding: 0.3rem 0.6rem; border-radius: var(--radius-sm); }
	}
	img { display: block; width: auto; max-width: 100%; object-fit: contain; }
</style>