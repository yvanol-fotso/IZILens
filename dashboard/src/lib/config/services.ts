import type { Component } from 'svelte';
import { Building2, Fingerprint, IdCard, Activity } from '@lucide/svelte';

export type ServiceId = 'kyc' | 'kyb' | 'liveness' | 'monitoring';
export interface ServiceDef { id: ServiceId; slug: string; icon: Component<any>; color: string }

/** Les quatre modules commerciaux (pages /services/<slug>). */
export const SERVICES: ServiceDef[] = [
	{ id: 'kyc', slug: 'kyc', icon: IdCard, color: 'var(--brand-blue)' },
	{ id: 'kyb', slug: 'kyb', icon: Building2, color: 'var(--accent-purple)' },
	{ id: 'liveness', slug: 'liveness-biometrics', icon: Fingerprint, color: 'var(--accent-mint)' },
	{ id: 'monitoring', slug: 'monitoring', icon: Activity, color: 'var(--accent-orange)' }
];
export const serviceBySlug = (slug: string) => SERVICES.find((s) => s.slug === slug);

/** Lien vers le formulaire de devis avec les services présélectionnés. */
export const quoteHref = (selected: string[] = []) => `/contact?type=quote${selected.length ? `&services=${selected.join(',')}` : ''}#form`;
export const demoHref = '/contact?type=demo#demo';
