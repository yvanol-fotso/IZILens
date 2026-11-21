import { loadDoc } from '$lib/server/markdown';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = ({ locals }) => ({ doc: loadDoc(locals.locale, 'terms') });
