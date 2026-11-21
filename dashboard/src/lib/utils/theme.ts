export type ThemeMode = 'light' | 'dark' | 'system';

export function applyTheme(mode: ThemeMode) {
	const resolved = mode === 'system' ? (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light') : mode;
	document.documentElement.setAttribute('data-theme', resolved);
	document.cookie = `izi_theme=${mode}; Path=/; Max-Age=${60 * 60 * 24 * 365}; SameSite=Lax`;
}

export function currentTheme(): 'light' | 'dark' {
	return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
}
