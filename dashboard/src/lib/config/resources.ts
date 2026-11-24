import type { Component } from 'svelte';
import type { Permission } from './permissions';

/**
 * Moteur de ressources : une définition TypeScript décrit une liste, ses filtres, ses formulaires,
 * ses actions et sa fiche détail. Les pages /admin/[resource] et /app/[resource] les rendent toutes.
 * Ces définitions sont aussi la SOURCE du contrat backend (docs/FRONTEND_CONTRACT.md, `npm run contract`).
 */
export type ColType = 'text' | 'mono' | 'date' | 'datetime' | 'money' | 'number' | 'percent' | 'status' | 'risk' | 'bool' | 'list' | 'badge' | 'file';
export interface Col { key: string; type?: ColType; link?: boolean; /** colonne portant la devise pour type=money */ currencyKey?: string }

export type FieldType = 'text' | 'textarea' | 'number' | 'select' | 'multiselect' | 'switch' | 'date' | 'email' | 'password' | 'url' | 'file' | 'repeater' | 'staff';
export interface Field {
	name: string; type: FieldType; options?: string[]; required?: boolean; hint?: string; min?: number; max?: number;
	/** file : types acceptés ; multiple : plusieurs fichiers */ accept?: string; multiple?: boolean;
	/** repeater : sous-champs (ex. dirigeants, bénéficiaires effectifs) */ fields?: Field[];
	/** valeur initiale depuis la fiche (édition) : clé de l'objet */ from?: string;
	/** champ secret : jamais ré-affiché, vide = inchangé */ secret?: boolean;
}

export interface Action {
	id: string; method: 'POST' | 'PATCH' | 'PUT' | 'DELETE'; path: string; permission: Permission;
	tone?: 'danger' | 'brand' | 'default';
	/** motif obligatoire (audit) */ reason?: boolean;
	/** action critique : demande un code MFA (step-up) en plus du motif */ critical?: boolean;
	fields?: Field[];
	/** n'afficher que si row[key] ∈ in */ when?: { key: string; in: string[] };
}
export interface Filter { key: string; type: 'search' | 'select' | 'range'; options?: string[] }
export interface Section { key: string; fields: { key: string; type?: ColType }[] }
export interface Related { key: string; path: string; cols: Col[] }

export interface ResourceDef {
	key: string; scope: 'admin' | 'client'; endpoint: string; read: Permission; icon?: Component<any>;
	cols: Col[]; filters?: Filter[]; pageSize?: number;
	create?: { permission: Permission; fields: Field[]; path?: string };
	/** réutilise create.fields pour PATCH endpoint/{id} */ edit?: boolean;
	actions?: Action[];
	/** false = pas de fiche détail (liste seule) */ detail?: false | { sections: Section[]; related?: Related[] };
	/** vers une page dédiée plutôt que la fiche générique (ex. revue KYC) */ detailHref?: string;
	exportable?: boolean;
}

export const exportHref = (def: ResourceDef, format: 'csv' | 'xlsx' | 'pdf', qs = '') => `/api/${def.scope === 'admin' ? 'admin' : 'v1'}${def.endpoint}/export?format=${format}${qs ? '&' + qs : ''}`;
export const humanize = (k: string) => k.replace(/[_\-.]/g, ' ').replace(/^./, (c) => c.toUpperCase());
