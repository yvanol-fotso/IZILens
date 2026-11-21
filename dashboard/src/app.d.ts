import type { Locale } from '$lib/i18n/locales';
import type { SessionUser } from '$lib/types';

declare global {
	namespace App {
		interface Locals {
			user: SessionUser | null;
			accessToken: string | null;
			locale: Locale;
			theme: string;
		}
		interface Error {
			message: string;
			code?: string;
		}
	}
}

export {};
