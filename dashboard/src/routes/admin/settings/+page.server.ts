import { CONFIG_PAGES } from '$lib/config/admin-config';
import { loadConfig, saveConfig } from '$lib/server/config-page';
import type { Actions, PageServerLoad } from './$types';

const page = CONFIG_PAGES.settings;
export const load: PageServerLoad = async (event) => ({ cfg: await loadConfig(event, page) });
export const actions: Actions = { save: (event) => saveConfig(event, page) };
