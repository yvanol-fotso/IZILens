<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	let { next = '' }: { next?: string } = $props();
	const { t } = getI18n();
	// Navigation complète (pas de fetch) : on quitte l'application pour accounts.google.com.
	const href = $derived(`/api/auth/oauth?provider=google${next ? `&next=${encodeURIComponent(next)}` : ''}`);
</script>

<a class="g" {href} data-sveltekit-reload>
	<svg width="20" height="20" viewBox="0 0 48 48" aria-hidden="true"><path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9.1 3.5l6.8-6.8C35.8 2.4 30.3 0 24 0 14.6 0 6.5 5.4 2.6 13.2l7.9 6.1C12.4 13.6 17.7 9.5 24 9.5z"/><path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.7c-.6 3-2.3 5.5-4.8 7.2l7.6 5.9c4.4-4.1 7-10.1 7-17.6z"/><path fill="#FBBC05" d="M10.5 28.7a14.5 14.5 0 0 1 0-9.4l-7.9-6.1a24 24 0 0 0 0 21.6l7.9-6.1z"/><path fill="#34A853" d="M24 48c6.5 0 11.9-2.1 15.9-5.8l-7.6-5.9c-2.1 1.4-4.9 2.3-8.3 2.3-6.3 0-11.6-4.1-13.5-9.8l-7.9 6.1C6.5 42.6 14.6 48 24 48z"/></svg>
	{t('auth.login.google')}
</a>

<style lang="scss">
	.g { display: flex; align-items: center; justify-content: center; gap: 0.75rem; padding: 0.8rem 1rem; border: 1.5px solid var(--border-strong); border-radius: var(--radius); background: var(--surface); color: var(--fg); font-weight: 700; font-size: var(--fs-sm); text-decoration: none !important; transition: border-color 0.15s, box-shadow 0.15s; &:hover { border-color: var(--primary); box-shadow: var(--shadow-md); } }
</style>
