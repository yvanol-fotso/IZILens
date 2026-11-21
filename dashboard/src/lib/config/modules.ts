import type { Component } from 'svelte';
import { FileCheck2, ScanFace, Fingerprint, ShieldAlert, KeyRound } from '@lucide/svelte';
import type { ModuleId, SessionUser } from '$lib/types';

export interface ModuleDef {
	id: ModuleId;
	/** live = branché au backend · soon = interface prête, backend à venir */
	status: 'live' | 'soon';
	icon: Component<any>;
	href: string;
}

export const MODULES: ModuleDef[] = [
	{ id: 'kyc', status: 'live', icon: FileCheck2, href: '/app/verifications' },
	{ id: 'liveness', status: 'soon', icon: ScanFace, href: '/app/liveness' },
	{ id: 'biometrics', status: 'soon', icon: Fingerprint, href: '/app/biometrics' },
	{ id: 'aml', status: 'soon', icon: ShieldAlert, href: '/app/aml' },
	{ id: 'api', status: 'live', icon: KeyRound, href: '/app/api-keys' }
];

export function moduleEnabled(user: SessionUser | null | undefined, id: ModuleId): boolean {
	if (!user) return false;
	if (user.role === 'super_admin') return true;
	const enabled = user.organization?.enabled_modules ?? ['kyc', 'api'];
	return enabled.includes(id);
}
