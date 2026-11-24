import { error } from '@sveltejs/kit';
import { serviceBySlug } from '$lib/config/services';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = ({ params }) => {
	const service = serviceBySlug(params.slug);
	if (!service) error(404, { message: 'not_found', code: 'not_found' });
	return { slug: service.slug };
};
