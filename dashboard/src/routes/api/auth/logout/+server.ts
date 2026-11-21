import { redirect, type RequestHandler } from '@sveltejs/kit';
import { logoutEverywhere } from '$lib/server/auth/service';
import { REFRESH_COOKIE } from '$lib/server/auth/session';

export const POST: RequestHandler = async ({ cookies, locals }) => {
	await logoutEverywhere(cookies, locals.accessToken, cookies.get(REFRESH_COOKIE));
	redirect(303, '/login?info=logged_out');
};
