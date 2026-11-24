import { accountActions, loadAccount } from '$lib/server/account';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => ({ account: await loadAccount(event), setup: event.url.searchParams.get('setup') === 'mfa' });
export const actions: Actions = { ...accountActions };
