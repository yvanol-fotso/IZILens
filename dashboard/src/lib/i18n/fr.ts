/**
 * Dictionnaire FR = source de vérité des clés.
 * `en.ts` doit avoir exactement la même forme (vérifié par TypeScript).
 */
const fr = {
	meta: {
		siteTitle: 'IZI LENS — Vérifiez les identités, bâtissez la confiance numérique',
		siteDescription:
			"Infrastructure de vérification d'identité et de conformité : documents, biométrie, risque et AML dans une seule plateforme modulaire.",
		app: 'Tableau de bord'
	},
	common: {
		save: 'Enregistrer',
		cancel: 'Annuler',
		delete: 'Supprimer',
		edit: 'Modifier',
		create: 'Créer',
		search: 'Rechercher',
		loading: 'Chargement…',
		back: 'Retour',
		next: 'Suivant',
		previous: 'Précédent',
		actions: 'Actions',
		details: 'Détails',
		copy: 'Copier',
		copied: 'Copié',
		all: 'Tous',
		none: 'Aucun',
		close: 'Fermer',
		confirm: 'Confirmer',
		optional: 'optionnel',
		refresh: 'Actualiser',
		view: 'Voir',
		filter: 'Filtrer',
		reset: 'Réinitialiser',
		learnMore: 'En savoir plus',
		page: 'Page {page} sur {pages}',
		results: '{count} résultat(s)',
		noData: 'Aucune donnée',
		unknown: 'Inconnu',
		never: 'Jamais',
		yes: 'Oui',
		no: 'Non',
		active: 'Actif',
		inactive: 'Inactif',
		name: 'Nom',
		date: 'Date',
		email: 'E-mail',
		role: 'Rôle',
		organization: 'Organisation',
		skipToContent: 'Aller au contenu'
	},
	nav: {
		platform: 'Plateforme',
		solutions: 'Solutions',
		coverage: 'Couverture',
		why: 'Pourquoi IZI LENS',
		industries: 'Secteurs',
		resources: 'Ressources',
		company: 'Entreprise',
		developers: 'Développeurs',
		signIn: 'Se connecter',
		getStarted: 'Commencer',
		contactSales: 'Contacter les ventes',
		openApp: 'Ouvrir le tableau de bord',
		menu: 'Menu',
		language: 'Langue',
		theme: 'Thème',
		themeLight: 'Clair',
		themeDark: 'Sombre',
		themeSystem: 'Système'
	},
	solutions: {
		groups: {
			verification: 'Vérification',
			compliance: 'Conformité',
			platform: 'Plateforme'
		},
		items: {
			identity: "Vérification d'identité",
			document: 'Vérification de documents',
			biometric: 'Vérification biométrique',
			liveness: 'Détection de vivacité',
			aml: 'Filtrage AML',
			sanctions: 'Filtrage des sanctions',
			pep: 'Filtrage PEP',
			media: 'Presse défavorable',
			api: 'Intégration API',
			analytics: 'Tableau de bord et analyses',
			security: 'Sécurité et confidentialité',
			coverage: 'Couverture mondiale'
		}
	},
	home: {
		hero: {
			title: "Vérifiez qui se présente, avant qu'il n'entre.",
			subtitle:
				"Documents, biométrie, risque et conformité : une seule infrastructure pour savoir à qui vous avez affaire, en quelques secondes et sans friction pour vos clients.",
			primary: 'Parler à notre équipe',
			secondary: "Explorer l'API",
			demoTitle: 'Dossier KYC-20418',
			demoDocument: 'Document authentique',
			demoFace: 'Visage concordant',
			demoLiveness: 'Vivacité détectée',
			demoRisk: 'Risque faible',
			demoScan: 'Analyse en cours'
		},
		platform: {
			title: 'Un parcours complet, du document à la décision',
			subtitle:
				"Chaque étape fonctionne seule ou en chaîne. Activez uniquement les modules dont votre organisation a besoin.",
			steps: {
				collect: { title: 'Collecter', desc: 'Capturez et validez documents et données.' },
				verify: { title: 'Vérifier', desc: 'Authentifiez les identités avec des contrôles avancés.' },
				assess: { title: 'Évaluer', desc: 'Détectez les risques et les comportements suspects.' },
				act: { title: 'Décider', desc: 'Appliquez des règles et des flux configurables.' },
				integrate: { title: 'Intégrer', desc: 'Branchez la vérification via nos API et SDK.' }
			}
		},
		coverage: {
			title: 'Vérifiez vos utilisateurs partout dans le monde',
			subtitle:
				"Intégrez particuliers et entreprises dans plusieurs pays, avec une large gamme de documents et le respect des réglementations locales.",
			stats: {
				countries: { value: '200+', label: 'Pays et territoires' },
				docs: { value: '5 000+', label: "Types de documents d'identité" },
				compliance: { value: 'Global', label: 'Conformité réglementaire' },
				speed: { value: 'Rapide', label: 'Vérification en quelques secondes' }
			},
			docs: {
				passports: { title: 'Passeports', desc: 'Passeports de tous les grands pays.' },
				ids: { title: "Cartes d'identité", desc: "Cartes d'identité nationales officielles." },
				licenses: { title: 'Permis de conduire', desc: 'Permis locaux et internationaux.' },
				permits: { title: 'Titres de séjour', desc: 'Permis et cartes de résidence.' },
				business: { title: "Documents d'entreprise", desc: 'Documents de société et bénéficiaires effectifs.' }
			}
		},
		why: {
			title: 'Plus sûr, plus intelligent, plus simple',
			subtitle:
				"Technologie avancée, couverture mondiale et parcours fluide pour vérifier vos utilisateurs, réduire la fraude et accélérer votre croissance.",
			items: {
				fraud: { title: 'Prévention avancée de la fraude', desc: 'Des contrôles pilotés par IA pour détecter et bloquer les activités frauduleuses.' },
				coverage: { title: 'Couverture mondiale', desc: 'Vérifiez particuliers et entreprises dans de nombreux pays.' },
				speed: { title: 'Parcours rapide et fluide', desc: "Vérifiez vos utilisateurs en quelques secondes, sans friction." },
				flexible: { title: 'Flexible et évolutif', desc: "S'intègre facilement et s'adapte à votre métier." },
				compliance: { title: 'Pensé pour la conformité', desc: 'Restez conforme aux réglementations locales et aux standards mondiaux.' }
			}
		},
		cta: {
			title: 'Prêt à vérifier en toute confiance ?',
			subtitle:
				'Rejoignez les organisations qui font confiance à IZI LENS pour vérifier leurs utilisateurs, prévenir la fraude et rester conformes.',
			primary: 'Parler à notre équipe',
			secondary: "Voir la documentation de l'API",
			perks: {
				onboarding: { title: 'Mise en route rapide', desc: "Démarrez vite avec l'appui de notre équipe." },
				integration: { title: 'Intégration flexible', desc: 'Via notre API ou des outils simples.' },
				support: { title: 'Support dédié', desc: 'Nos experts vous accompagnent à chaque étape.' },
				partner: { title: 'Un partenaire durable', desc: 'Grandissez avec un partenaire fiable.' }
			}
		}
	},
	footer: {
		tagline:
			"IZI LENS aide les entreprises à vérifier les identités, à évaluer les risques et à créer des expériences numériques plus sûres grâce à des parcours de vérification configurables.",
		columns: {
			solutions: 'Solutions',
			industries: 'Secteurs',
			developers: 'Développeurs',
			company: 'Entreprise',
			legal: 'Légal et confidentialité',
			contact: 'Contact',
			social: 'Réseaux sociaux'
		},
		solutions: {
			identity: "Vérification d'identité",
			biometric: 'Vérification biométrique',
			kyb: "Vérification d'entreprise (KYB)",
			aml: 'AML et filtrage des risques',
			fraud: 'Prévention de la fraude',
			coverage: 'Couverture mondiale'
		},
		industries: {
			financial: 'Services financiers',
			fintech: 'Fintech',
			ecommerce: 'E-commerce et places de marché',
			crypto: 'Crypto et actifs numériques',
			mobility: 'Mobilité',
			platforms: 'Plateformes en ligne'
		},
		links: { docs: "Documentation de l'API", signIn: 'Connexion au tableau de bord', contact: 'Nous contacter' },
		privacy: 'Politique de confidentialité',
		terms: "Conditions d'utilisation",
		cookies: 'Politique de cookies',
		cookiePrefs: 'Préférences de cookies',
		rights: 'Tous droits réservés.',
		language: 'Langue'
	},
	cookieBanner: {
		title: 'Cookies et technologies similaires',
		text: "Nous utilisons des cookies et des technologies similaires pour assurer le fonctionnement du site, mémoriser vos préférences, comprendre son utilisation et activer certaines fonctionnalités facultatives. Vous pouvez accepter les cookies facultatifs, les refuser ou personnaliser vos choix.",
		acceptAll: 'Tout accepter',
		rejectAll: 'Refuser les cookies facultatifs',
		customize: 'Personnaliser',
		preferences: 'Préférences de cookies',
		preferencesText: 'Choisissez les catégories facultatives que vous autorisez. Vous pouvez modifier ou retirer votre consentement à tout moment.',
		save: 'Enregistrer mes préférences',
		alwaysActive: 'Toujours actif',
		version: 'Version {version} · en vigueur le {date}',
		necessary: { title: 'Strictement nécessaires', desc: 'Indispensables au fonctionnement du site, à la sécurité et à la mémorisation de vos choix de consentement.' },
		functional: { title: 'Fonctionnels', desc: 'Fonctionnalités facultatives et mémorisation de préférences au-delà du strict nécessaire.' },
		analytics: { title: 'Analytiques', desc: "Mesure de l'utilisation du site, soumise au consentement requis." },
		performance: { title: 'Performance', desc: "Outils de mesure ou d'optimisation des performances, distincts de l'analytique." },
		advertising: { title: 'Publicité et suivi', desc: 'Stockage publicitaire et suivi, uniquement si de telles technologies sont déployées.' },
		unclassified: { title: 'Non classés', desc: "Technologies en cours d'examen, en attente de classification." }
	},
	legal: {
		updated: 'Dernière mise à jour : {date}',
		toc: 'Sur cette page',
		manageCookies: 'Gérer mes préférences de cookies',
		draftNotice: 'Ce document est un projet destiné à être validé par votre conseil juridique avant publication.'
	},
	auth: {
		brand: {
			title: "Un seul tableau de bord pour toutes vos vérifications d'identité",
			points: {
				one: 'Dossiers KYC, revue humaine et traçabilité complète',
				two: 'Modules activables : vivacité, biométrie, AML',
				three: 'Isolation stricte des données par organisation'
			}
		},
		login: {
			title: 'Connexion',
			subtitle: 'Accédez à votre espace IZI LENS.',
			email: 'Adresse e-mail',
			password: 'Mot de passe',
			submit: 'Se connecter',
			noAccount: 'Pas encore de compte ?',
			signUp: 'Créer un compte',
			or: 'ou',
			google: 'Continuer avec Google',
			registered: 'Compte créé. Vous pouvez maintenant vous connecter.',
			loggedOut: 'Vous avez été déconnecté.',
			sessionExpired: 'Votre session a expiré. Reconnectez-vous.'
		},
		register: {
			title: 'Créer un compte',
			subtitle: 'Commencez en moins de deux minutes.',
			fullName: 'Nom complet',
			email: 'Adresse e-mail',
			password: 'Mot de passe',
			passwordHint: '12 caractères minimum.',
			confirm: 'Confirmer le mot de passe',
			submit: 'Créer mon compte',
			haveAccount: 'Déjà un compte ?',
			signIn: 'Se connecter',
			terms: "En continuant, vous acceptez nos conditions d'utilisation et notre politique de confidentialité."
		},
		errors: {
			invalid: 'E-mail ou mot de passe incorrect.',
			generic: "Une erreur est survenue. Réessayez dans un instant.",
			required: 'Ce champ est obligatoire.',
			email: 'Saisissez une adresse e-mail valide.',
			passwordShort: 'Le mot de passe doit contenir au moins 12 caractères.',
			passwordMismatch: 'Les mots de passe ne correspondent pas.',
			locked: 'Compte temporairement verrouillé après trop de tentatives.',
			unreachable: 'Le service est momentanément injoignable.',
			oauth_failed: 'La connexion avec Google a échoué. Réessayez.',
			oauth_unavailable: "La connexion avec Google n'est pas configurée.",
			oauth_denied: 'Aucun compte autorisé pour cette adresse Google.'
		}
	},
	app: {
		groups: { main: 'Principal', modules: 'Modules', workspace: 'Espace de travail', admin: 'Administration Kafintech' },
		nav: {
			overview: "Vue d'ensemble",
			verifications: 'Vérifications',
			newVerification: 'Nouvelle vérification',
			liveness: 'Vivacité',
			biometrics: 'Biométrie',
			aml: 'Filtrage AML',
			analytics: 'Analyses',
			apiKeys: 'Clés API',
			team: 'Équipe',
			audit: "Journal d'audit",
			settings: 'Paramètres',
			developers: 'Développeurs',
			admin: 'Administration',
			adminOverview: 'Synthèse',
			tenants: 'Organisations',
			members: 'Membres',
			announcements: 'Annonces',
			system: 'Système'
		},
		signOut: 'Se déconnecter',
		account: 'Mon compte',
		soonBadge: 'Bientôt',
		openMenu: 'Ouvrir le menu',
		backend: { ok: 'Service opérationnel', down: 'Service injoignable' }
	},
	dashboard: {
		welcome: 'Bonjour, {name}',
		subtitle: "Voici l'activité de vérification de votre organisation.",
		stats: {
			total: 'Dossiers',
			pending: 'À réviser',
			approved: 'Approuvés',
			rejected: 'Rejetés',
			confidence: 'Confiance OCR moyenne',
			highRisk: 'Risque élevé',
			approvalRate: "Taux d'approbation"
		},
		volume: 'Dossiers sur 14 jours',
		byStatus: 'Répartition par statut',
		byRisk: 'Répartition par risque',
		recent: 'Derniers dossiers',
		viewAll: 'Tout voir',
		modules: 'Modules',
		quickActions: 'Actions rapides',
		empty: { title: 'Aucun dossier pour le moment', desc: 'Soumettez un premier document pour voir apparaître vos statistiques.' }
	},
	verifications: {
		title: 'Vérifications',
		subtitle: "Tous les dossiers KYC soumis par votre organisation.",
		new: 'Nouvelle vérification',
		searchPlaceholder: 'Référence ou identifiant…',
		allStatuses: 'Tous les statuts',
		allRisks: 'Tous les risques',
		columns: { reference: 'Référence', type: 'Document', status: 'Statut', risk: 'Risque', confidence: 'Confiance OCR', date: 'Soumis le' },
		empty: { title: 'Aucun dossier trouvé', desc: 'Modifiez vos filtres ou soumettez une nouvelle vérification.' },
		upload: {
			title: 'Soumettre un document',
			subtitle: "Le document est analysé automatiquement ; les cas incertains passent en revue humaine.",
			docType: 'Type de document',
			reference: 'Votre référence interne',
			referenceHint: 'Facultatif. Sert à retrouver le dossier dans votre système.',
			front: 'Recto du document',
			back: 'Verso du document',
			backHint: 'Facultatif. Stocké pour la revue, non lu par l’OCR.',
			dropHint: 'Glissez une image ici ou cliquez pour choisir',
			sizeHint: 'JPEG, PNG ou WebP · 8 Mo maximum',
			submit: 'Lancer la vérification',
			success: 'Dossier créé. Analyse en cours.',
			fileRequired: 'Le recto du document est obligatoire.'
		},
		detail: {
			extracted: 'Données extraites',
			noExtracted: "Aucune donnée n'a pu être extraite.",
			flags: 'Signaux de risque',
			noFlags: 'Aucun signal de risque détecté.',
			documents: 'Documents',
			ocr: 'Confiance OCR',
			risk: 'Niveau de risque',
			created: 'Soumis',
			processed: 'Analysé',
			decided: 'Décidé',
			failure: 'Motif de l’échec',
			decisionTitle: 'Décision de revue',
			decisionHint: 'La décision est définitive et enregistrée dans le journal d’audit.',
			approve: 'Approuver',
			reject: 'Rejeter',
			reason: 'Motif de la décision',
			reasonPlaceholder: 'Expliquez brièvement votre décision…',
			reasonRequired: 'Un motif est requis pour rejeter un dossier.',
			decisionDone: 'Décision enregistrée.',
			alreadyDecided: 'Ce dossier a déjà fait l’objet d’une décision.',
			notPending: "Ce dossier n'est pas en attente de revue.",
			triggerLiveness: 'Demander une vérification de vivacité',
			front: 'Recto',
			back: 'Verso',
			sharpness: 'Netteté',
			fields: {
				surname: 'Nom',
				given_names: 'Prénoms',
				full_name: 'Nom complet',
				birth_date: 'Date de naissance',
				birth_place: 'Lieu de naissance',
				sex: 'Sexe',
				height: 'Taille',
				profession: 'Profession',
				document_number: 'N° du document',
				id_number: 'N° du document',
				issue_date: 'Délivré le',
				expiry_date: "Date d'expiration",
				father: 'Père',
				mother: 'Mère',
				nationality: 'Nationalité'
			}
		}
	},
	liveness: {
		title: 'Vivacité',
		subtitle: "Lorsqu'un dossier dépasse un seuil de risque, demandez à la personne de se filmer depuis son téléphone.",
		howTitle: 'Comment ça marche',
		steps: {
			one: 'Le seuil de risque est atteint ou vous lancez la demande manuellement.',
			two: 'Un lien sécurisé (ou un QR code) est envoyé sur le téléphone de la personne.',
			three: 'Elle suit le parcours guidé : visage, mouvement, lumière.',
			four: 'Le résultat revient dans le dossier et alimente la décision.'
		},
		generate: {
			title: 'Générer un lien de vérification',
			caseRef: 'Référence du dossier (optionnel)',
			button: 'Générer le lien',
			linkLabel: 'Lien à envoyer',
			scan: 'Scannez ce QR code avec un téléphone',
			expires: 'Valable {minutes} minutes',
			demo: "Mode démonstration : le module de vivacité du backend n'est pas encore branché.",
			error: 'Impossible de créer la session.'
		},
		threshold: {
			title: 'Déclenchement automatique',
			desc: 'Demander la vivacité automatiquement à partir de ce niveau de risque.',
			off: 'Désactivé',
			medium: 'Risque moyen et plus',
			high: 'Risque élevé uniquement',
			saved: 'Seuil enregistré.'
		},
		mobile: {
			title: 'Vérification de vivacité',
			intro: 'Placez votre visage dans le cadre, dans un endroit bien éclairé. Cela prend moins de 30 secondes.',
			start: 'Commencer',
			permission: "Autorisez l'accès à la caméra pour continuer.",
			prompts: {
				center: 'Regardez droit devant vous',
				left: 'Tournez lentement la tête à gauche',
				right: 'Tournez lentement la tête à droite',
				blink: 'Clignez des yeux'
			},
			capture: 'Capturer',
			done: 'Merci, vérification envoyée.',
			doneText: 'Vous pouvez fermer cette page et revenir à votre démarche.',
			invalid: 'Ce lien est invalide ou a expiré.'
		}
	},
	modules: {
		status: { live: 'Actif', soon: 'Bientôt', disabled: 'Non activé' },
		kyc: { title: 'Vérification de documents', desc: 'OCR, contrôles de qualité, signaux de risque et revue humaine.' },
		liveness: { title: 'Détection de vivacité', desc: "Prouvez que la personne est bien présente, en direct." },
		biometrics: { title: 'Biométrie faciale', desc: 'Comparez le visage au portrait du document.' },
		aml: { title: 'Filtrage AML', desc: 'Sanctions, PEP et presse défavorable.' },
		api: { title: 'API et clés', desc: 'Intégrez la vérification à vos produits.' },
		soon: {
			badge: 'Module en préparation',
			desc: 'Ce module est prévu dans le tableau de bord et sera relié au backend dès sa mise en service.',
			planned: 'Prévu'
		},
		biometrics_page: {
			title: 'Biométrie faciale',
			subtitle: 'Comparaison visage / document et score de similarité.',
			features: {
				match: 'Comparaison du selfie avec le portrait du document',
				score: 'Score de similarité et seuils configurables',
				quality: 'Contrôle de la qualité du visage',
				link: 'Résultat rattaché au dossier KYC'
			}
		},
		aml_page: {
			title: 'Filtrage AML',
			subtitle: 'Sanctions, personnes politiquement exposées et presse défavorable.',
			features: {
				sanctions: 'Listes de sanctions internationales',
				pep: 'Personnes politiquement exposées (PEP)',
				media: 'Recherche de presse défavorable',
				rules: 'Règles de risque configurables par organisation'
			}
		},
		announcements_page: {
			title: 'Annonces',
			subtitle: 'Messages diffusés aux organisations clientes.',
			features: {
				banner: "Bandeau d'information dans le tableau de bord",
				target: 'Ciblage par organisation ou par module',
				schedule: 'Planification et expiration'
			}
		}
	},
	analytics: {
		title: 'Analyses',
		subtitle: 'Tendances calculées sur les 200 derniers dossiers.',
		confidence: 'Distribution de la confiance OCR',
		daily: 'Volume quotidien',
		bands: { low: 'Moins de 70 %', mid: '70 – 90 %', high: 'Plus de 90 %' }
	},
	apiKeys: {
		title: 'Clés API',
		subtitle: 'Accès programmatique à vos vérifications. Chaque clé est liée à votre organisation.',
		create: 'Créer une clé',
		name: 'Nom de la clé',
		namePlaceholder: 'Ex. Application mobile — production',
		expiry: 'Expiration',
		expiryNever: 'Jamais',
		expiry30: '30 jours',
		expiry90: '90 jours',
		expiry365: '1 an',
		columns: { name: 'Nom', prefix: 'Préfixe', created: 'Créée le', lastUsed: 'Dernier usage', expires: 'Expire le', status: 'État' },
		revoke: 'Révoquer',
		revokeConfirm: "Révoquer la clé « {name} » ? Les applications qui l'utilisent cesseront de fonctionner.",
		revoked: 'Révoquée',
		expired: 'Expirée',
		created: 'Clé créée',
		showOnce: "Copiez cette clé maintenant : elle ne sera plus jamais affichée.",
		empty: { title: "Aucune clé API", desc: 'Créez une clé pour appeler l’API depuis vos applications.' }
	},
	team: {
		title: 'Équipe',
		subtitle: "Les membres de votre organisation et leurs rôles.",
		invite: 'Ajouter un membre',
		fullName: 'Nom complet',
		tempPassword: 'Mot de passe temporaire',
		tempPasswordHint: '12 caractères minimum. À communiquer au membre.',
		columns: { member: 'Membre', role: 'Rôle', status: 'État', lastLogin: 'Dernière connexion' },
		deactivate: 'Désactiver',
		activate: 'Réactiver',
		added: 'Membre ajouté.',
		updated: 'Membre mis à jour.',
		roleHelp: {
			admin: 'Gère clés, équipe et paramètres.',
			reviewer: 'Examine les dossiers et rend les décisions.',
			viewer: 'Consulte les dossiers en lecture seule.',
			integration: 'Compte technique pour les intégrations.'
		}
	},
	audit: {
		title: "Journal d'audit",
		subtitle: 'Historique en ajout seul de toutes les actions sensibles.',
		columns: { date: 'Date', actor: 'Acteur', action: 'Action', resource: 'Ressource', ip: 'Adresse IP' },
		empty: { title: "Aucune entrée d'audit", desc: "Les actions apparaîtront ici dès qu'elles auront lieu." },
		actors: { user: 'Utilisateur', api_key: 'Clé API', system: 'Système' }
	},
	settings: {
		title: 'Paramètres',
		subtitle: 'Votre profil, vos préférences et la sécurité de votre compte.',
		profile: { title: 'Profil', fullName: 'Nom complet', email: 'E-mail', saved: 'Profil mis à jour.' },
		preferences: { title: 'Préférences', language: "Langue de l'interface", theme: 'Thème' },
		organization: { title: 'Organisation', slug: 'Identifiant', modules: 'Modules activés', readonly: "Contactez Kafintech pour modifier les modules de votre organisation." },
		security: {
			title: 'Sécurité',
			currentPassword: 'Mot de passe actuel',
			newPassword: 'Nouveau mot de passe',
			change: 'Changer le mot de passe',
			changed: 'Mot de passe mis à jour.',
			googleNote: 'Connecté avec Google ? Votre mot de passe est géré par Google.'
		}
	},
	developers: {
		title: 'Développeurs',
		subtitle: "Appelez l'API IZI LENS depuis vos applications en trois étapes.",
		step1: 'Créez une clé API',
		step1Text: 'Depuis la page Clés API. Elle ne s’affiche qu’une seule fois.',
		step2: 'Soumettez un document',
		step3: 'Lisez le résultat',
		docs: "Documentation complète de l'API",
		baseUrl: "URL de base",
		health: 'État du service'
	},
	admin: {
		title: 'Administration Kafintech',
		subtitle: 'Espace réservé aux super-administrateurs de la plateforme.',
		stats: { tenants: 'Organisations', members: 'Membres', activeTenants: 'Organisations actives' },
		recentActivity: 'Activité récente',
		tenants: {
			title: 'Organisations',
			subtitle: 'Les clients de la plateforme et les modules qui leur sont ouverts.',
			create: 'Nouvelle organisation',
			slug: 'Identifiant (slug)',
			slugHint: 'Minuscules, chiffres et tirets.',
			adminEmail: "E-mail du premier administrateur",
			modules: 'Modules',
			columns: { name: 'Organisation', slug: 'Identifiant', modules: 'Modules', status: 'État', created: 'Créée le' },
			created: 'Organisation créée.',
			updated: 'Organisation mise à jour.',
			suspend: 'Suspendre',
			reactivate: 'Réactiver',
			detail: "Détail de l'organisation",
			members: 'Membres de l’organisation',
			noMembers: 'Aucun membre.'
		},
		members: { title: 'Membres', subtitle: 'Tous les utilisateurs de la plateforme.', org: 'Organisation' },
		system: {
			title: 'Système',
			subtitle: "État du backend et configuration de l'environnement.",
			backend: 'Service backend',
			baseUrl: 'URL du service',
			oidc: 'Connexion Google (OIDC)',
			configured: 'Configurée',
			missing: 'Non configurée',
			loginFormat: 'Format de connexion'
		}
	},
	status: {
		processing: 'En cours',
		pending_review: 'À réviser',
		approved: 'Approuvé',
		rejected: 'Rejeté',
		failed: 'Échec'
	},
	risk: { low: 'Faible', medium: 'Moyen', high: 'Élevé', none: 'Non évalué' },
	roles: {
		super_admin: 'Super-administrateur',
		admin: 'Administrateur',
		reviewer: 'Réviseur',
		viewer: 'Lecteur',
		integration: 'Intégration'
	},
	docTypes: { cni_cm: "Carte nationale d'identité (Cameroun)" },
	errors: {
		forbidden: "Vous n'avez pas accès à cette page.",
		notFound: 'Cette page est introuvable.',
		backend_unreachable: 'Le service backend est injoignable. Vérifiez BACKEND_SERVICE_URL.',
		generic: 'Une erreur est survenue.',
		goHome: "Retour à l'accueil",
		goDashboard: 'Retour au tableau de bord'
	},
	toast: { saved: 'Modifications enregistrées.', error: "L'action a échoué.", copied: 'Copié dans le presse-papiers.' }
};

export default fr;
export type Dictionary = typeof fr;
