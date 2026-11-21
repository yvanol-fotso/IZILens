import { writable } from 'svelte/store';

export type ToastTone = 'success' | 'error' | 'info';
export interface Toast { id: number; message: string; tone: ToastTone }

let counter = 0;
const { subscribe, update } = writable<Toast[]>([]);

export const toasts = { subscribe };

export function toast(message: string, tone: ToastTone = 'info', duration = 4200) {
	const id = ++counter;
	update((all) => [...all, { id, message, tone }]);
	if (typeof window !== 'undefined') setTimeout(() => dismiss(id), duration);
	return id;
}
export const toastSuccess = (m: string) => toast(m, 'success');
export const toastError = (m: string) => toast(m, 'error', 6000);
export function dismiss(id: number) {
	update((all) => all.filter((t) => t.id !== id));
}
