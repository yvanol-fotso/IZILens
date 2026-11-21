import { error } from '@sveltejs/kit';
import { marked } from 'marked';
import type { Locale } from '$lib/i18n/locales';

const files = import.meta.glob('/src/content/*/*.md', { query: '?raw', import: 'default', eager: true }) as Record<string, string>;

export interface LegalDoc {
	title: string;
	updated: string;
	html: string;
	toc: { id: string; text: string }[];
}

const slugify = (s: string) =>
	s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

function frontmatter(raw: string): { meta: Record<string, string>; body: string } {
	const m = raw.match(/^---\n([\s\S]*?)\n---\n?/);
	if (!m) return { meta: {}, body: raw };
	const meta: Record<string, string> = {};
	for (const line of m[1].split('\n')) {
		const i = line.indexOf(':');
		if (i > 0) meta[line.slice(0, i).trim()] = line.slice(i + 1).trim().replace(/^["']|["']$/g, '');
	}
	return { meta, body: raw.slice(m[0].length) };
}

/**
 * Charge /src/content/<locale>/<slug>.md. Le contenu est du Markdown de confiance (versionné dans le dépôt) :
 * on peut donc le faire réécrire/mettre à jour par une IA sans toucher au code.
 */
export function loadDoc(locale: Locale, slug: string): LegalDoc {
	const raw = files[`/src/content/${locale}/${slug}.md`] ?? files[`/src/content/fr/${slug}.md`];
	if (!raw) error(404, { message: 'not_found', code: 'not_found' });
	const { meta, body } = frontmatter(raw);
	const toc: LegalDoc['toc'] = [];
	let html = marked.parse(body, { async: false }) as string;
	html = html.replace(/<h([23])>(.*?)<\/h\1>/g, (_m, level: string, inner: string) => {
		const text = inner.replace(/<[^>]+>/g, '');
		const id = slugify(text);
		if (level === '2') toc.push({ id, text });
		return `<h${level} id="${id}">${inner}</h${level}>`;
	});
	return { title: meta.title ?? slug, updated: meta.updated ?? '', html, toc };
}
