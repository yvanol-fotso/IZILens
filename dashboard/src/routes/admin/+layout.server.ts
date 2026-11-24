import { redirect } from '@sveltejs/kit';
import { requireStaff } from '$lib/server/guards';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = (event) => {
	const user = requireStaff(event);
	// MFA obligatoire pour le personnel (le backend l'impose aussi) : inscription forcée tant qu'elle n'est pas active.
	if (user.mfa_enabled === false && !event.url.pathname.startsWith('/admin/account')) redirect(303, '/admin/account?setup=mfa');
	return { user };
};
