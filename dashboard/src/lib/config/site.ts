/** Coordonnées publiques. Contact : aucun téléphone ni adresse détaillée publics (décision validée). */
export const SITE = {
	name: 'IZI LENS',
	company: 'Kafintech Group',
	email: 'contact@izilens.com',
	/** URL officielles à confirmer : tant que `url` est null, l'icône n'est PAS affichée. */
	social: [
		{ id: 'linkedin', label: 'LinkedIn', url: null as string | null },
		{ id: 'facebook', label: 'Facebook', url: null as string | null },
		{ id: 'instagram', label: 'Instagram', url: null as string | null },
		{ id: 'x', label: 'X (Twitter)', url: null as string | null }
	]
} as const;
