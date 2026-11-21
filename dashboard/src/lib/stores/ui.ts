import { writable } from 'svelte/store';

/** Tiroir latéral mobile du tableau de bord et du site vitrine. */
export const sidebarOpen = writable(false);
export const mobileNavOpen = writable(false);
