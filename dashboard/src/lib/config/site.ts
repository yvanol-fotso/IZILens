export const SITE = {
	name: 'IZI LENS',
	company: 'Kafintech Group' /* à confirmer : « Inc. » est-il le suffixe officiel ? */,
	email: 'contact@izilens.com',
	phone: '+1 825 963 6493',
	address: ['305 - 14903 93 AVE NW', 'Edmonton, Alberta T5R 5H1', 'Canada'] /* à vérifier sur les registres officiels */,
	/** URL officielles à confirmer : tant que `url` est null, l'icône n'est PAS affichée. */
	social: [
		{ id: 'linkedin', label: 'LinkedIn', url: null as string | null },
		{ id: 'facebook', label: 'Facebook', url: null as string | null },
		{ id: 'instagram', label: 'Instagram', url: null as string | null },
		{ id: 'x', label: 'X (Twitter)', url: null as string | null }
	]
} as const;
