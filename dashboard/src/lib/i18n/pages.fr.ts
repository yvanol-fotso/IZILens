/** Contenus éditoriaux du site public (source : documents de contenu validés). FR = source des clés. */
const pages = {
	nav: {
		home: 'Accueil',
		services: 'Services',
		solutions: 'Solutions',
		developers: 'Développeurs',
		resources: 'Ressources',
		about: 'À propos',
		contact: 'Contact',
		signIn: 'Se connecter',
		demo: 'Demander une démonstration',
		menu: 'Menu',
		language: 'Langue',
		theme: 'Thème',
		themeLight: 'Clair',
		themeDark: 'Sombre',
		themeSystem: 'Système',
		openApp: 'Ouvrir le tableau de bord'
	},
	site: {
		slogan: 'Building trust in every digital interaction.',
		byline: 'by Kafintech Group'
	},
	footer: {
		about: "IZI LENS est une plateforme technologique de vérification d'identité et d'entreprise développée par Kafintech Group.",
		columns: { platform: 'Plateforme', developers: 'Développeurs', company: 'Entreprise', legal: 'Informations légales' },
		links: { home: 'Accueil', services: 'Nos services', solutions: 'Solutions', pricing: 'Tarifs', developers: 'Espace développeurs', resources: 'Ressources', about: 'À propos', contact: 'Contact', demo: 'Demander une démonstration', signIn: 'Connexion client' },
		privacy: 'Politique de confidentialité',
		terms: "Conditions générales d'utilisation",
		cookies: 'Politique relative aux cookies',
		cookiePrefs: 'Préférences de cookies',
		copyright: '© {year} IZI LENS – A Kafintech Group Company. Tous droits réservés.'
	},
	common: {
		quote: 'Demander un devis',
		customQuote: 'Obtenir un devis personnalisé',
		demo: 'Demander une démonstration',
		learnMore: 'En savoir plus',
		discover: 'Découvrir',
		features: 'Fonctionnalités principales',
		useCases: "Cas d'utilisation",
		servicesFor: 'Services adaptés',
		selected: '{count} service(s) sélectionné(s)',
		planned: 'Fonctionnalités prévues',
		comingSoon: 'Bientôt disponible'
	},
	svcNames: {
		kyc: 'KYC — Vérification d’identité',
		kyb: 'KYB — Vérification des entreprises',
		liveness: 'Liveness & Biometrics — Vérification biométrique',
		monitoring: 'Monitoring & Suivi — Supervision des vérifications'
	},
	home: {
		hero: {
			title: 'Vérifiez les identités. Renforcez la confiance numérique.',
			text1: "IZI LENS est une plateforme internationale de vérification d'identité et d'entreprise conçue pour accompagner les organisations dans la sécurisation de leurs interactions numériques.",
			text2: "Grâce à une approche modulaire combinant vérification KYC, KYB, biométrie et monitoring, IZI LENS vous permet de mieux connaître vos utilisateurs, vérifier vos partenaires commerciaux et renforcer vos processus de confiance numérique.",
			primary: 'Demander une démonstration',
			secondary: 'Découvrir nos services',
			demoTitle: 'Dossier KYC-20418',
			demoScan: 'Analyse en cours',
			demoDocument: 'Document authentique',
			demoFace: 'Visage concordant',
			demoLiveness: 'Vivacité détectée',
			demoRisk: 'Risque faible'
		},
		intro: {
			title: "La confiance numérique commence par une identité vérifiée.",
			p1: "Dans un monde où les interactions numériques se multiplient, vérifier l'identité des personnes et l'authenticité des entreprises est devenu un enjeu essentiel.",
			p2: "IZI LENS met à disposition une plateforme technologique conçue pour simplifier les processus de vérification, améliorer la connaissance de vos utilisateurs et contribuer à la prévention des risques liés aux identités frauduleuses.",
			p3: "Que vous soyez une banque, une fintech, une institution de microfinance, une compagnie d'assurance ou une entreprise numérique, nos solutions vous accompagnent dans la construction d'un environnement numérique plus sûr et plus fiable.",
			p4: "Notre ambition : rendre la vérification d'identité plus accessible, plus fluide et plus facilement intégrable dans les parcours numériques, partout dans le monde."
		},
		services: {
			title: 'Des solutions modulaires adaptées à vos besoins.',
			text: "Avec IZI LENS, vous choisissez les services qui correspondent aux exigences de votre organisation. Activez un module individuellement ou combinez plusieurs solutions pour construire votre dispositif de vérification.",
			button: 'Choisir mes services'
		},
		why: {
			title: 'Une plateforme pensée pour les exigences du numérique.',
			items: {
				modular: { title: 'Une approche modulaire', desc: "Sélectionnez uniquement les services dont votre organisation a besoin. Combinez les différentes solutions selon vos processus et exigences." },
				simple: { title: 'Une expérience simplifiée', desc: "Facilitez les parcours de vérification de vos utilisateurs grâce à une expérience pensée pour limiter les étapes inutiles." },
				integrable: { title: 'Une technologie intégrable', desc: "Connectez les fonctionnalités d'IZI LENS à vos applications et systèmes existants grâce à une architecture orientée API." },
				visibility: { title: 'Une meilleure visibilité opérationnelle', desc: "Suivez les vérifications, consultez les statuts et accédez aux événements importants depuis vos outils de gestion." },
				security: { title: 'Une approche axée sur la sécurité', desc: "La protection des informations et la maîtrise des accès constituent des éléments essentiels de la conception de la plateforme." },
				international: { title: 'Une ambition internationale', desc: "Accompagnez vos activités sur différents marchés grâce à une plateforme conçue pour répondre à des environnements numériques variés." }
			}
		},
		how: {
			title: 'De la collecte à la vérification, un parcours simplifié.',
			steps: {
				s1: { title: 'Collecte des informations', desc: "L'utilisateur transmet les informations et documents nécessaires à sa vérification." },
				s2: { title: 'Analyse et vérification', desc: "Les contrôles prévus sont effectués sur les documents, les données et, selon le parcours, les éléments biométriques." },
				s3: { title: 'Évaluation et revue', desc: "Les résultats sont traités selon les règles définies. Les cas nécessitant une intervention peuvent être orientés vers une revue manuelle." },
				s4: { title: 'Résultat et suivi', desc: "Consultez le statut de la vérification et retrouvez les événements associés depuis votre environnement IZI LENS." }
			}
		},
		sectors: {
			title: "Une solution conçue pour plusieurs secteurs d'activité.",
			text: "IZI LENS accompagne les organisations confrontées aux enjeux d'identification, de connaissance client et de confiance numérique.",
			button: 'Explorer nos solutions sectorielles',
			items: {
				banks: { title: 'Banques et institutions financières', desc: 'Identification des clients et vérification des entreprises.' },
				fintech: { title: 'Fintech et paiement', desc: 'Vérification des utilisateurs et sécurisation des parcours numériques.' },
				micro: { title: 'Microfinance', desc: 'Identification des clients et vérification des dossiers.' },
				insurance: { title: 'Assurances', desc: 'Vérification des souscripteurs et des informations fournies.' },
				telecom: { title: 'Télécommunications', desc: 'Identification et vérification des abonnés.' },
				ecommerce: { title: 'E-commerce et marketplaces', desc: 'Vérification des vendeurs et partenaires commerciaux.' },
				platforms: { title: 'Plateformes numériques', desc: 'Vérification des utilisateurs et prévention de la fraude.' }
			}
		},
		api: {
			title: 'Intégrez la vérification directement dans vos applications.',
			p1: "Avec IZI LENS, les entreprises et les équipes techniques peuvent intégrer des fonctionnalités de vérification dans leurs propres applications et parcours numériques.",
			p2: "Notre approche orientée API vise à faciliter la connexion entre votre environnement informatique et les services de vérification IZI LENS.",
			p3: "Que vous développiez une application fintech, une plateforme de paiement ou un système de gestion client, vous pouvez concevoir une intégration adaptée à votre architecture.",
			primary: 'Explorer notre API',
			secondary: 'Accéder à la documentation développeur'
		},
		security: {
			title: 'La sécurité au cœur de notre approche.',
			lead: "Les données d'identité et les informations d'entreprise nécessitent une attention particulière.",
			text: "IZI LENS accorde une importance essentielle à la sécurité des traitements, à la gestion des accès, à la traçabilité des opérations et à la protection des informations traitées par la plateforme.",
			intro: 'Notre approche repose notamment sur :',
			points: [
				"La gestion contrôlée des accès et des autorisations.",
				'La protection des informations et des documents.',
				'La traçabilité des opérations sensibles.',
				'La séparation des environnements techniques.',
				'La prise en compte des exigences applicables en matière de protection des données.'
			],
			closing: 'La confiance numérique commence par une gestion responsable des données.'
		},
		pricing: {
			title: 'Une tarification flexible, adaptée à votre organisation.',
			p1: "Chaque organisation possède des besoins, des volumes et des exigences différents.",
			p2: "IZI LENS propose une approche tarifaire flexible permettant de sélectionner les services nécessaires et de choisir une formule adaptée à son activité.",
			p3: "Selon vos besoins, vous pourrez accéder à des offres structurées ou solliciter une proposition commerciale personnalisée.",
			intro: 'Notre approche tarifaire :',
			points: [
				'Services disponibles individuellement.',
				'Formules combinant plusieurs services.',
				'Tarification adaptée aux volumes de vérification.',
				'Propositions commerciales personnalisées.',
				"Possibilité d'étudier des besoins spécifiques d'intégration."
			],
			primary: 'Consulter nos tarifs',
			secondary: 'Obtenir une offre personnalisée'
		},
		cta: {
			title: 'Prêt à renforcer la confiance dans vos opérations numériques ?',
			p1: "Découvrez comment IZI LENS peut accompagner votre organisation dans ses processus de vérification d'identité et d'entreprise.",
			p2: "Présentez-nous votre activité, vos besoins et les services qui vous intéressent. Notre équipe pourra vous proposer une démonstration adaptée à votre organisation.",
			primary: 'Demander une démonstration',
			secondary: 'Configurer mon offre'
		}
	},
	svc: {
		hero: {
			kicker: 'The right verification solutions for your business.',
			title: 'Nos services',
			text1: "IZI LENS propose une suite de solutions de vérification d’identité et d’entreprise conçues pour aider les organisations à renforcer la confiance dans leurs interactions numériques.",
			text2: "De la vérification des particuliers à l’identification des entreprises, en passant par la biométrie et le suivi des vérifications, nos services s’adaptent aux besoins de votre activité.",
			primary: 'Découvrir nos solutions',
			secondary: 'Demander un devis'
		},
		overview: {
			title: 'Des solutions adaptées à vos exigences de vérification',
			text: "Chaque entreprise possède ses propres exigences en matière d’identification, de sécurité et de vérification. IZI LENS vous permet de sélectionner librement les services dont vous avez besoin et de construire une solution adaptée à votre organisation.",
			mainTitle: 'Nos quatre services principaux',
			note: 'Chaque service dispose de sa propre page détaillée avec ses fonctionnalités, ses cas d’utilisation et ses possibilités d’intégration.'
		},
		items: {
			kyc: {
				code: 'KYC', name: 'Know Your Customer',
				short: "Vérification de l’identité des personnes physiques à travers la collecte et l’analyse des informations et documents d’identité.",
				title: "Vérification d'identité",
				tagline: "Vérifiez l’identité de vos utilisateurs et simplifiez vos processus d’intégration numérique.",
				intro: "Le service KYC d’IZI LENS permet aux entreprises de collecter et d’examiner les informations d’identité de leurs clients à travers un processus structuré.",
				problem: "Intégrer rapidement des utilisateurs sans multiplier les étapes, tout en gardant la maîtrise des informations et des documents collectés.",
				features: [
					'Collecte des informations personnelles.', 'Téléchargement ou capture des documents d’identité.', 'Contrôle de la qualité et de la lisibilité des documents.',
					'Extraction des informations par reconnaissance de caractères (OCR), lorsque disponible.', 'Vérification de la cohérence des données collectées.', 'Gestion des statuts de vérification.',
					"Demande de correction ou d’informations complémentaires.", 'Possibilité de revue manuelle des dossiers.'
				],
				useCases: ['Ouverture de comptes numériques.', 'Inscription sur des plateformes financières.', 'Onboarding des utilisateurs de fintech.', "Identification des clients d’institutions de microfinance.", 'Vérification des utilisateurs de plateformes digitales.'],
				benefits: ['Parcours d’intégration plus fluide.', 'Dossiers structurés, statuts et historique consultables.', 'Revue manuelle pour les cas incertains.'],
				faq: [
					{ q: "Que se passe-t-il si un document est illisible ?", a: "Le contrôle de qualité le signale et une correction ou des informations complémentaires peuvent être demandées." },
					{ q: "Une décision humaine est-elle possible ?", a: "Oui. Les dossiers nécessitant une intervention peuvent être orientés vers une revue manuelle." }
				],
				cta: 'Découvrir le service KYC'
			},
			kyb: {
				code: 'KYB', name: 'Know Your Business',
				short: "Vérification des entreprises, de leurs documents légaux, de leurs représentants et de leurs bénéficiaires effectifs.",
				title: 'Vérification des entreprises',
				tagline: "Connaissez les entreprises avec lesquelles vous établissez des relations commerciales ou financières.",
				intro: "Le service KYB d’IZI LENS permet de structurer la vérification des entreprises, de leurs documents juridiques et des personnes qui les représentent.",
				problem: "Savoir précisément qui se cache derrière une entreprise : documents légaux, dirigeants et bénéficiaires effectifs.",
				features: [
					"Collecte des informations sur l’entreprise.", 'Collecte et examen des documents légaux.', 'Identification des dirigeants et représentants légaux.', 'Identification des bénéficiaires effectifs (UBO).',
					'Consultation de la structure de propriété déclarée.', 'Identification des informations manquantes.', 'Gestion des demandes de compléments.', 'Historique et suivi des vérifications.'
				],
				useCases: ['Onboarding de clients professionnels.', 'Ouverture de comptes entreprises.', 'Vérification des commerçants et marchands.', 'Intégration de fournisseurs et partenaires.', 'Vérification des entreprises clientes de plateformes financières.'],
				benefits: ['Vision claire des personnes liées à l’entreprise.', 'Informations manquantes identifiées dès le départ.', 'Historique complet des vérifications.'],
				faq: [
					{ q: "Quels éléments sont examinés ?", a: "Les informations de l’entreprise, ses documents légaux, ses représentants et ses bénéficiaires effectifs (UBO), selon le périmètre convenu." },
					{ q: "Peut-on demander des compléments ?", a: "Oui, la gestion des demandes de compléments fait partie du service." }
				],
				cta: 'Découvrir le service KYB'
			},
			liveness: {
				code: 'Liveness & Biometrics', name: 'Biométrie et détection de présence réelle',
				short: "Vérification biométrique et contrôle de présence réelle afin de renforcer la fiabilité des processus d’identification.",
				title: 'Biométrie et détection de présence réelle',
				tagline: 'Renforcez la fiabilité de vos vérifications d’identité.',
				intro: "Ce service ajoute une étape biométrique au processus de vérification afin de contribuer à confirmer que la personne présentée correspond à l’identité soumise et qu’elle est réellement présente lors du contrôle, selon les fonctionnalités activées.",
				problem: "S’assurer que la personne derrière l’écran est bien celle du document, et qu’elle est présente en direct.",
				features: [
					"Capture d’image du visage.", "Contrôle de la qualité de l’image.", 'Vérification de présence réelle (liveness).', 'Comparaison faciale lorsque cette fonctionnalité est disponible et activée.',
					'Contrôles contre certaines tentatives de présentation frauduleuse.', 'Restitution des résultats ou scores disponibles.', 'Possibilité de revue complémentaire en cas de résultat incertain.'
				],
				useCases: ['Vérification à distance des utilisateurs.', 'Ouverture de comptes financiers.', 'Authentification renforcée.', 'Validation d’opérations sensibles.', "Parcours d’identification nécessitant un contrôle biométrique."],
				benefits: ['Fiabilité accrue des vérifications à distance.', 'Résultats et scores disponibles dans le dossier.', 'Revue complémentaire en cas de doute.'],
				faq: [
					{ q: "La comparaison faciale est-elle toujours active ?", a: "Elle est proposée lorsque la fonctionnalité est disponible et activée pour votre organisation." },
					{ q: "Que faire si le résultat est incertain ?", a: "Une revue complémentaire peut être déclenchée." }
				],
				cta: 'Découvrir Liveness & Biometrics'
			},
			monitoring: {
				code: 'Monitoring & Suivi', name: 'Supervision des vérifications',
				short: "Suivi des demandes de vérification, consultation des statuts, historique des événements et gestion des alertes opérationnelles.",
				title: 'Supervision des vérifications',
				tagline: 'Gardez une visibilité sur vos processus de vérification.',
				intro: "Le service Monitoring d’IZI LENS permet aux organisations de suivre leurs demandes de vérification et de consulter leur évolution à travers une interface de supervision.",
				problem: "Savoir où en est chaque dossier, repérer ceux qui sont bloqués et garder une trace des actions effectuées.",
				features: [
					'Suivi des demandes de vérification.', 'Consultation des statuts : en attente, en cours, validé, rejeté ou nécessitant une intervention.', 'Historique des événements.', 'Traçabilité des actions effectuées.',
					'Alertes opérationnelles.', 'Identification des dossiers en attente.', 'Recherche et filtrage des demandes.', 'Consultation des résultats et de leur évolution.'
				],
				useCases: ['Supervision des opérations KYC et KYB.', 'Suivi des dossiers clients.', 'Gestion des vérifications en attente.', 'Contrôle opérationnel des processus d’identification.', "Consultation de l’historique des vérifications."],
				benefits: ['Visibilité opérationnelle de bout en bout.', 'Dossiers en attente identifiés rapidement.', 'Historique et traçabilité consultables.'],
				faq: [
					{ q: "Monitoring surveille-t-il les transactions financières ?", a: "Non. Il concerne le suivi fonctionnel des demandes de vérification et ne constitue pas, à lui seul, un moteur de surveillance des transactions ni de détection du blanchiment de capitaux." },
					{ q: "Peut-on filtrer les demandes ?", a: "Oui, la recherche et le filtrage des demandes sont prévus." }
				],
				note: "Précision importante : le service Monitoring présenté ici concerne le suivi fonctionnel des demandes de vérification. Il ne constitue pas, à lui seul, un moteur complet de surveillance des transactions financières ou de détection des opérations de blanchiment de capitaux.",
				cta: 'Découvrir Monitoring & Suivi'
			}
		},
		detail: { problem: 'Problématique', benefits: 'Bénéfices pour les entreprises', integration: "Possibilités d'intégration", faq: 'Questions fréquentes', back: 'Tous les services', integrationText: "Selon les fonctionnalités disponibles et le périmètre convenu : API, SDK lorsque disponibles, Webhooks pour les événements et workflows de vérification configurables." },
		compose: { title: 'Vous choisissez. Nous adaptons la solution.', text: "Avec IZI LENS, vous n’êtes pas obligé de souscrire à l’ensemble des services. Sélectionnez uniquement les modules correspondant à vos besoins opérationnels.", button: 'Demander un devis personnalisé' },
		sectors: { title: "Des solutions pour plusieurs secteurs d’activité", text: "IZI LENS accompagne les organisations qui souhaitent intégrer des processus fiables de vérification et d’identification dans leurs activités.", note: "Les services proposés peuvent être combinés selon les exigences de chaque secteur et les besoins de chaque organisation." },
		integration: {
			title: 'Intégrez IZI LENS à votre environnement numérique.',
			text: "Nos solutions sont conçues pour s’intégrer aux systèmes et applications des entreprises à travers des interfaces techniques adaptées.",
			intro: "Selon les fonctionnalités disponibles et le périmètre convenu, l’intégration peut notamment s’appuyer sur :",
			list: ['Des API.', 'Des SDK, lorsque disponibles.', "Des Webhooks pour la transmission d’événements.", 'Des workflows de vérification configurables.'],
			primary: 'Explorer notre API', secondary: 'Contacter notre équipe technique'
		},
		pricing: {
			title: 'Une offre adaptée à votre organisation.',
			text: "Chaque entreprise possède des volumes, des contraintes et des besoins différents. IZI LENS propose une approche tarifaire personnalisée afin de construire une offre correspondant à votre utilisation.",
			intro: 'Le tarif est établi sur devis, en fonction notamment :',
			list: ['Des services sélectionnés.', 'Du volume prévisionnel de vérifications.', 'Des pays et marchés concernés.', 'Des fonctionnalités demandées.', 'Des besoins d’intégration technique.', 'Du niveau d’accompagnement souhaité.']
		},
		final: { title: 'Construisons ensemble votre solution de vérification.', text: "Que vous souhaitiez vérifier des particuliers, identifier des entreprises, renforcer vos contrôles biométriques ou superviser vos processus de vérification, IZI LENS vous accompagne dans la mise en place d’une solution adaptée." }
	},
	sol: {
		hero: {
			kicker: 'Verification solutions built around your business.',
			title: 'Des solutions de vérification adaptées à votre secteur, partout dans le monde.',
			text1: "Chaque organisation possède ses propres exigences en matière d’identification, de vérification et de confiance numérique.",
			text2: "IZI LENS accompagne les entreprises et institutions à l’échelle internationale avec des solutions modulaires permettant de vérifier les personnes physiques, les entreprises, de renforcer les contrôles biométriques et de superviser les processus de vérification.",
			primary: 'Explorer nos solutions', secondary: 'Demander une démonstration'
		},
		intro: {
			title: 'Une plateforme. Plusieurs secteurs. Une approche internationale.',
			p1: "IZI LENS met à disposition des organisations une suite de services conçus pour répondre aux besoins de vérification et d'identification de différents secteurs d'activité.",
			p2: "Notre plateforme s'adresse notamment aux institutions financières, aux fintechs, aux entreprises de paiement, aux assureurs, aux opérateurs télécoms et aux plateformes numériques.",
			p3: "Grâce à son architecture modulaire, chaque organisation peut sélectionner librement les services correspondant à ses besoins.",
			modulesTitle: 'Nos quatre modules :',
			modules: ['KYC — Vérification des personnes physiques.', 'KYB — Vérification des entreprises.', 'Liveness & Biometrics — Vérification biométrique et présence réelle.', 'Monitoring — Suivi et supervision des vérifications.']
		},
		sectorsTitle: "Solutions par secteur d'activité",
		needs: 'Besoins couverts',
		sectors: {
			banks: { name: 'Banques et institutions financières', tagline: "Renforcez vos processus d'identification et d'intégration des clients.", desc: "Les établissements financiers doivent pouvoir identifier leurs clients, recueillir les informations nécessaires et organiser leurs processus de vérification. IZI LENS permet de structurer ces étapes à travers des parcours adaptés aux exigences opérationnelles de chaque établissement.", needs: ["Vérification de l'identité des clients particuliers.", 'Vérification des entreprises clientes.', 'Contrôles biométriques complémentaires.', 'Suivi des demandes de vérification.', "Consultation de l'historique des contrôles."] },
			fintech: { name: 'Fintechs et entreprises de paiement', tagline: "Simplifiez l'intégration de vos utilisateurs et structurez vos vérifications.", desc: "Les fintechs et les entreprises de paiement ont besoin de parcours d'inscription numériques adaptés à leurs utilisateurs et aux marchés sur lesquels elles opèrent. IZI LENS permet d'intégrer des étapes de vérification dans leurs applications et plateformes.", needs: ['Identification des nouveaux utilisateurs.', 'Collecte et vérification des documents.', 'Vérification biométrique selon le parcours choisi.', 'Identification des entreprises partenaires ou marchandes.', 'Suivi des demandes et de leurs statuts.', 'Intégration avec les systèmes existants.'] },
			micro: { name: 'Institutions de microfinance', tagline: 'Structurez l\'identification de vos clients et partenaires.', desc: "Les institutions de microfinance accueillent des particuliers, des entrepreneurs et des organisations aux profils variés. IZI LENS permet de mettre en place des processus structurés de vérification pour accompagner leur transformation numérique.", needs: ['Identification des clients particuliers.', "Vérification des documents d'identité.", 'Vérification des entreprises et organisations clientes.', 'Contrôles biométriques complémentaires.', 'Suivi des dossiers de vérification.', "Consultation de l'historique des contrôles."] },
			insurance: { name: "Compagnies d'assurance", tagline: "Renforcez la fiabilité de vos parcours d'identification.", desc: "Les compagnies d'assurance peuvent utiliser IZI LENS pour structurer les étapes d'identification de leurs assurés, intermédiaires et partenaires.", needs: ["Vérification de l'identité des assurés.", 'Vérification des représentants et partenaires professionnels.', 'Contrôles biométriques selon les besoins.', 'Suivi des demandes de vérification.', 'Traçabilité des événements liés aux dossiers.'] },
			telecom: { name: 'Télécommunications', tagline: "Accompagnez vos parcours d'identification numérique.", desc: "Les opérateurs télécoms et fournisseurs de services numériques peuvent intégrer des processus de vérification pour structurer l'identification de leurs utilisateurs et partenaires.", needs: ['Vérification des identités individuelles.', 'Collecte et examen des documents.', 'Vérification des entreprises partenaires.', 'Contrôles biométriques complémentaires.', 'Suivi des demandes de vérification.'] },
			ecommerce: { name: 'E-commerce et marketplaces', tagline: 'Construisez un environnement numérique plus fiable pour vos utilisateurs et vendeurs.', desc: "Les plateformes de commerce en ligne peuvent avoir besoin de vérifier différents profils : acheteurs, vendeurs professionnels, marchands et partenaires. IZI LENS permet de mettre en place des parcours adaptés à ces profils.", needs: ['Vérification des utilisateurs.', 'Vérification des vendeurs et marchands professionnels.', "Identification des représentants d'entreprises.", 'Contrôles biométriques selon le niveau de vérification souhaité.', 'Suivi des dossiers et des résultats.'] },
			platforms: { name: 'Plateformes numériques et entreprises technologiques', tagline: 'Intégrez la vérification directement dans vos parcours numériques.', desc: "Les entreprises qui développent des applications et des services en ligne peuvent intégrer les fonctionnalités d'IZI LENS dans leurs propres environnements.", needs: ['Vérification des utilisateurs à distance.', 'Vérification des comptes professionnels.', 'Intégration des contrôles biométriques.', 'Automatisation de certaines étapes selon les workflows configurés.', 'Suivi des demandes et consultation des résultats.', 'Connexion aux systèmes existants via API.'] }
		},
		modular: { title: "Vous choisissez les services dont votre entreprise a besoin.", text: "IZI LENS ne vous impose pas une formule unique. Vous pouvez sélectionner un seul service ou combiner plusieurs modules en fonction de vos activités et de vos exigences opérationnelles.", hint: 'Vous pouvez commencer avec un service et faire évoluer votre configuration selon vos besoins.', button: 'Composer ma solution' },
		intl: { kicker: 'Building trust across borders.', title: 'Une plateforme à vocation internationale', p1: "Les organisations évoluent dans des environnements de plus en plus internationaux. Leurs clients, partenaires et utilisateurs peuvent se trouver dans différents pays.", p2: "IZI LENS est conçue pour accompagner les entreprises opérant sur plusieurs marchés, avec une approche modulaire et des possibilités d'intégration adaptées à leurs environnements numériques.", p3: "Notre ambition est de faciliter la mise en place de processus de vérification cohérents dans différents contextes géographiques.", primary: 'Découvrir nos services', secondary: 'Contacter notre équipe' },
		tech: { title: 'Connectez IZI LENS à votre environnement numérique.', text: "IZI LENS est conçue pour s'intégrer aux applications et systèmes des organisations.", intro: "Selon les fonctionnalités disponibles et le périmètre technique retenu, les possibilités d'intégration peuvent comprendre :", list: ['API pour connecter les fonctionnalités de vérification.', "SDK lorsque disponibles pour faciliter l'intégration.", 'Webhooks pour recevoir les événements liés aux vérifications.', 'Workflows configurables selon les parcours retenus.'], note: "Notre équipe peut accompagner l'étude de vos besoins d'intégration.", primary: 'Explorer notre documentation développeur', secondary: 'Parler à notre équipe technique' },
		why: { title: 'Une approche pensée pour les organisations modernes.', items: { modularity: { title: 'Modularité', desc: 'Sélectionnez les services correspondant à vos besoins.' }, adaptability: { title: 'Adaptabilité', desc: 'Construisez des parcours de vérification adaptés à votre secteur.' }, integration: { title: 'Intégration', desc: 'Connectez les fonctionnalités à vos applications et systèmes existants.' }, visibility: { title: 'Visibilité opérationnelle', desc: "Suivez l'évolution de vos demandes de vérification." }, reach: { title: 'Portée internationale', desc: 'Une plateforme conçue pour accompagner des organisations opérant sur différents marchés.' } } },
		final: { title: 'Votre activité mérite une solution de vérification adaptée.', text: "Que vous soyez une banque, une fintech, une institution de microfinance, une compagnie d'assurance ou une plateforme numérique, IZI LENS vous accompagne dans la construction d'une solution adaptée à vos exigences opérationnelles et techniques." }
	},
	dev: {
		hero: { kicker: 'Powerful verification APIs. Seamless integration.', title: "Intégrez la vérification d'identité et d'entreprise directement dans vos applications.", text1: "IZI LENS met à disposition des développeurs et des entreprises un environnement technique conçu pour connecter les fonctionnalités KYC, KYB, Liveness & Biometrics et Monitoring à leurs propres applications et systèmes.", text2: "Grâce à nos interfaces de programmation et à nos outils d'intégration, construisez des parcours de vérification adaptés à votre environnement technique.", primary: 'Demander un accès développeur', secondary: 'Se connecter' },
		intro: { title: 'Tout ce qu’il faut pour intégrer la vérification numérique.', text: "Que vous développiez une application financière, une plateforme de paiement, un service numérique ou un système interne, IZI LENS vous permet de connecter des fonctionnalités de vérification à votre infrastructure existante.", intro: "L'environnement développeur est organisé autour de plusieurs composants :", list: ['API de vérification.', "SDK, selon les langages et environnements pris en charge.", 'Webhooks pour la réception des événements.', 'Documentation technique sécurisée.', 'Environnement Sandbox pour les tests.', 'Environnement Production pour les opérations réelles.', 'Gestion des accès et des identifiants API.'] },
		apisTitle: 'Nos interfaces API',
		apis: {
			kyc: { name: 'KYC API', tag: 'Identity Verification', desc: 'Intégrez la vérification des personnes physiques dans vos applications.', list: ["Création d'une demande de vérification KYC.", "Transmission des informations d'identité.", 'Soumission des documents.', "Consultation du statut d'une vérification.", 'Récupération des résultats disponibles.', 'Gestion des demandes nécessitant une intervention.'] },
			kyb: { name: 'KYB API', tag: 'Business Verification', desc: 'Connectez les fonctionnalités de vérification des entreprises à vos systèmes.', list: ["Création d'une demande KYB.", "Transmission des informations de l'entreprise.", 'Soumission des documents légaux.', 'Gestion des dirigeants et représentants.', 'Collecte des informations relatives aux bénéficiaires effectifs (UBO).', 'Consultation des statuts et résultats disponibles.'] },
			bio: { name: 'Liveness & Biometrics API', tag: 'Biometrics', desc: 'Ajoutez des contrôles biométriques à vos parcours de vérification.', list: ["Initialisation d'une session biométrique.", 'Capture des données nécessaires au contrôle.', 'Vérification de présence réelle.', 'Comparaison faciale lorsque disponible.', 'Consultation des résultats et informations de vérification.'] },
			mon: { name: 'Monitoring API', tag: 'Monitoring', desc: 'Connectez les informations de suivi des vérifications à vos outils internes.', list: ['Consultation du statut des demandes.', "Suivi de l'évolution des vérifications.", 'Consultation des événements disponibles.', 'Accès aux informations de suivi autorisées.', 'Intégration des événements dans les systèmes internes.'] }
		},
		publishRule: "Seuls les éléments effectivement développés, testés et validés sont présentés comme opérationnels. Les fonctionnalités listées ci-dessus sont prévues et seront ouvertes progressivement.",
		sdk: { title: 'SDK et outils d’intégration', text: "IZI LENS vise à faciliter l'intégration de ses services dans différents environnements de développement. Les SDK permettront de simplifier certaines opérations d'intégration et de communication avec les API.", note: "Les langages et environnements seront affichés en fonction des SDK effectivement développés et publiés." },
		webhooks: { title: 'Webhooks', text: "Les Webhooks permettent à votre application de recevoir des notifications lorsqu'un événement lié à une vérification survient. Ils facilitent l'automatisation des processus internes et la synchronisation entre IZI LENS et vos systèmes.", eventsTitle: "Exemples d'événements", events: ['Demande de vérification créée.', 'Vérification démarrée.', 'Document soumis.', 'Vérification terminée.', 'Résultat disponible.', 'Vérification nécessitant une intervention.'] },
		docs: { title: 'Documentation technique', text: "La documentation technique complète est destinée aux développeurs et aux équipes d'intégration. Elle est accessible uniquement aux utilisateurs disposant d'un compte développeur et ayant ouvert une session.", topics: ['Getting Started', 'Authentication', 'KYC API', 'KYB API', 'Biometrics API', 'Monitoring API', 'Webhooks', 'Errors & Responses'] },
		access: {
			title: "Processus d'accès aux API",
			steps: { s1: { title: 'Créer un compte', desc: "Le développeur ou l'entreprise remplit le formulaire d'inscription et fournit les informations demandées." }, s2: { title: "Se connecter à l'espace développeur", desc: "Après la création de son compte, l'utilisateur accède à son espace sécurisé et à la documentation technique." }, s3: { title: "Demander l'accès API", desc: "L'utilisateur précise son organisation, son projet d'intégration, les services souhaités (KYC, KYB, Biometrics ou Monitoring), l'utilisation envisagée et les informations techniques nécessaires." }, s4: { title: 'Validation et activation', desc: "L'équipe IZI LENS examine la demande. Après validation, les accès API autorisés sont activés et les identifiants correspondants sont mis à disposition dans l'espace développeur." } },
			note: "La création d'un compte ne signifie donc pas que les accès API de production sont automatiquement activés."
		},
		env: { title: 'Développez, testez et déployez en confiance.', sandbox: { name: 'Sandbox — Environnement de test', desc: "Permet de tester vos intégrations sans effectuer de vérifications opérationnelles réelles.", list: ['Tests des connexions API.', 'Simulation des parcours de vérification.', 'Utilisation de données de test.', 'Tests des Webhooks.', 'Simulation de réponses et de statuts.'] }, prod: { name: 'Production — Environnement opérationnel', desc: "Permet d'utiliser les services IZI LENS dans un contexte opérationnel, après validation des accès.", list: ['Utilisation des identifiants de production.', 'Transmission des demandes réelles.', 'Consultation des résultats selon les autorisations.', 'Réception des événements opérationnels.', 'Suivi des demandes de vérification.'] }, note: 'Les identifiants et les données Sandbox et Production sont distincts et séparés.' },
		security: { title: 'La sécurité fait partie de l’intégration.', list: ['Authentification des requêtes API.', 'Protection et gestion des clés API.', 'Communication sécurisée entre systèmes.', 'Contrôle des permissions.', 'Journalisation des événements techniques.', 'Séparation des environnements de test et de production.', 'Accès administrateurs avec authentification multifacteur (MFA) : TOTP et passkeys, selon le périmètre retenu.'] },
		support: { title: 'Besoin d’accompagnement ?', text: "Vous avez un projet d'intégration spécifique ? Notre équipe peut échanger avec vos développeurs afin de comprendre vos besoins techniques et identifier l'approche d'intégration adaptée.", primary: 'Demander un accès développeur', secondary: 'Contacter notre équipe technique' }
	},
	res: {
		hero: { title: 'Explorez le centre de ressources IZI LENS', subtitle: 'Analyses, guides et ressources pour vous aider à bâtir des expériences numériques sûres et à renforcer la confiance.' },
		searchLabel: 'Rechercher dans les ressources', searchPlaceholder: 'Rechercher une question, un guide, un sujet…',
		rubriques: {
			blog: { title: 'Blog & Actualités', desc: "Articles rédigés par IZI LENS et actualités externes sélectionnées, avec attribution et lien vers la source.", items: ['KYC & Identity Verification', 'KYB & Business Verification', 'Biometrics & Liveness', 'AML & Compliance', 'Fraud Prevention', 'Fintech & Digital Identity', 'Digital Trust & Security'] },
			guides: { title: 'Guides & E-books', desc: "Guides gratuits en accès direct ; contenus premium après un court formulaire professionnel.", items: ['The Complete Guide to KYC Verification', 'Understanding KYB and Business Verification', 'Biometrics and Liveness Detection Explained', 'How to Build a Digital Identity Verification Process', 'Fraud Prevention in Digital Financial Services', 'KYC Compliance for Fintech Companies'] },
			api: { title: 'Documentation & API Resources', desc: "Ressources introductives publiques. La documentation technique complète reste privée, après création d'un compte développeur et validation des accès.", items: ['Présentation des API IZI LENS', "Introduction à l'intégration", 'Guides techniques introductifs', "Exemples d'intégration", 'Webhooks disponibles', 'Environnements Sandbox et Production'] },
			cases: { title: 'Case Studies & Use Cases', desc: "Scénarios sectoriels illustratifs. Aucun témoignage ni résultat client n'est publié sans autorisation et preuve.", items: ['Banques et institutions financières', 'Fintech et sociétés de paiement', 'Institutions de microfinance', 'Assurances', 'Télécommunications', 'E-commerce et marketplaces', 'Plateformes numériques'] },
			security: { title: 'Security & Compliance Resources', desc: "Ressources sur la sécurité et la confiance numérique. Aucune certification n'est présentée comme acquise tant qu'elle n'est pas obtenue et vérifiée.", items: ['Data Protection', 'Identity Verification Security', 'Document Verification', 'Biometric Security', 'Fraud Prevention', 'Compliance Resources', 'Privacy & Data Governance'] }
		},
		soon: 'Premiers contenus bientôt publiés',
		faq: { title: 'Questions fréquentes', empty: 'Aucune question ne correspond à votre recherche.', categories: { general: 'Général', kyc: 'KYC', kyb: 'KYB', bio: 'Biométrie & Liveness', api: 'API & intégration' }, items: [
			{ c: 'general', q: "Qu'est-ce qu'IZI LENS ?", a: "IZI LENS est une plateforme internationale de vérification d'identité et d'entreprise, modulaire : KYC, KYB, biométrie et monitoring." },
			{ c: 'kyc', q: "Qu'est-ce que la vérification KYC ?", a: "Le KYC (Know Your Customer) consiste à collecter, analyser et vérifier les informations et documents d'identité d'une personne." },
			{ c: 'kyb', q: 'Quelle différence entre KYC et KYB ?', a: "Le KYC vérifie des personnes physiques ; le KYB vérifie des entreprises, leurs documents légaux, leurs représentants et leurs bénéficiaires effectifs." },
			{ c: 'bio', q: 'Comment fonctionne la vérification biométrique ?', a: "Elle ajoute une capture du visage, un contrôle de présence réelle et, lorsque la fonctionnalité est activée, une comparaison faciale avec le document." },
			{ c: 'general', q: 'Comment demander une démonstration ?', a: "Utilisez le bouton « Demander une démonstration » : notre équipe commerciale examine votre demande et vous contacte." },
			{ c: 'api', q: "Comment accéder à l'API ?", a: "Créez un compte développeur, puis soumettez une demande d'accès. Les accès sont activés après validation par l'équipe IZI LENS." }
		] },
		dev: { title: 'Pour les développeurs', text: "Découvrez l'environnement technique et demandez un accès au portail développeur sécurisé.", primary: 'Accéder au portail développeur' },
		cta: { title: 'Une question sur la vérification d’identité ?', primary: 'Demander une démonstration', secondary: 'Contacter notre équipe' }
	},
	about: {
		hero: { kicker: 'Our Story', title: "D'une vision canadienne à un écosystème technologique international" },
		story: ["Fondé au Canada, Kafintech Group Inc. est un groupe diversifié qui développe des initiatives dans les domaines des technologies, des services financiers, des paiements numériques et des médias.", "Depuis sa création, le groupe poursuit une ambition : concevoir et développer des solutions innovantes capables de répondre aux nouveaux besoins des entreprises, des particuliers et des marchés en pleine transformation numérique.", "Au fil de son développement, Kafintech Group a progressivement étendu ses activités au-delà du marché canadien, notamment vers plusieurs marchés africains, à travers différentes marques, sociétés et initiatives spécialisées.", "Cette évolution a permis de construire un écosystème regroupant des activités complémentaires dans les transferts internationaux, les solutions de paiement, la microfinance, les technologies financières, les systèmes de point de vente et les médias.", "C'est dans cette dynamique de diversification et d'innovation qu'IZI LENS a été développé : une plateforme spécialisée dans la vérification d'identité numérique, le KYC, le KYB, la biométrie et les technologies de confiance numérique.", "Aujourd'hui, Kafintech Group poursuit son développement avec une ambition internationale : construire un écosystème technologique et financier capable d'accompagner les transformations de l'économie numérique."],
		eco: { kicker: 'Our Ecosystem', title: 'Un écosystème diversifié. Une vision commune.', text: "Kafintech Group développe plusieurs marques et initiatives complémentaires dans différents secteurs.", items: [
			{ n: 'IZI LIFE PAY', d: "Solutions de transferts internationaux d'argent et de paiements numériques." },
			{ n: 'IZI TRUST CAPITAL', d: "Activités de microfinance, d'épargne et de financement." },
			{ n: 'IZI FLOW', d: "Infrastructure d'agrégation et d'intégration de solutions de paiement." },
			{ n: 'IZI ONE', d: 'Solutions de point de vente et outils de gestion des paiements.' },
			{ n: 'IZI LENS', d: "Plateforme de vérification d'identité numérique, KYC, KYB et confiance numérique." },
			{ n: 'IZI VOXES', d: 'Médias, communication et production de contenus.' },
			{ n: 'DIASPO ECO', d: "Magazine consacré à l'entrepreneuriat et à l'économie de la diaspora." },
			{ n: 'KAFINTECH — AFRICAN MARKETS', d: "Développement d'activités et de représentations sur plusieurs marchés africains, notamment au Bénin, au Burkina Faso, en Côte d'Ivoire, au Togo et en République démocratique du Congo." }
		] },
		leadership: { kicker: 'Our Leadership', title: 'Des équipes expérimentées. Une ambition partagée.', text: "La croissance de Kafintech Group repose sur des équipes multidisciplinaires engagées dans le développement technologique, la gestion financière, les opérations, la conformité et le développement commercial.", intro: "La présentation institutionnelle de l'équipe dirigeante mettra en avant les responsabilités suivantes :", roles: ['Direction administrative et financière.', 'Direction technique.', 'Direction commerciale.', 'Conseil stratégique.'], note: "Les noms, fonctions officielles, biographies et portraits des responsables autorisés à être présentés seront intégrés dans cette section." },
		ambition: { kicker: 'Our Global Ambition', title: 'Développé au Canada. Conçu pour les marchés mondiaux.', p1: "Depuis ses bases canadiennes, Kafintech Group poursuit une stratégie de développement tournée vers les marchés internationaux.", p2: "Le groupe entend construire des solutions technologiques et financières évolutives, capables de répondre aux besoins de différents secteurs et de contribuer à une économie numérique plus accessible, connectée et fiable." }
	},
	contact: {
		hero: { title: 'Parlons de votre projet.', text: "Vous souhaitez découvrir IZI LENS, intégrer nos solutions de vérification d'identité ou discuter d'un partenariat ? Notre équipe est à votre disposition pour étudier votre besoin.", primary: 'Contacter notre équipe', secondary: 'Demander une démonstration' },
		cardsTitle: 'Nos différents contacts',
		cards: {
			sales: { title: 'Service commercial', tag: 'Sales', desc: "Pour les entreprises qui souhaitent découvrir nos services, obtenir une proposition commerciale ou discuter de leurs besoins en KYC, KYB, biométrie et monitoring.", cta: 'Écrire au service commercial' },
			partners: { title: 'Partenariats', tag: 'Partnerships', desc: "Pour les fournisseurs technologiques, institutions financières, distributeurs et organisations intéressés par une collaboration avec IZI LENS.", cta: 'Proposer un partenariat' },
			demo: { title: 'Démonstration', tag: 'Request a Demo', desc: "Les prospects peuvent demander une présentation personnalisée de la plateforme. L'équipe commerciale examine la demande et organise un échange si nécessaire.", cta: 'Demander une démonstration' },
			support: { title: 'Support technique', tag: 'Technical Support', desc: "Le support technique est réservé aux clients disposant d'un compte IZI LENS. L'accès s'effectue exclusivement depuis le portail client sécurisé : soumission des demandes, signalement d'incident et suivi des tickets.", cta: 'Accéder au portail client' }
		},
		form: {
			title: 'Envoyez-nous votre demande.', text: "Complétez le formulaire ci-dessous. Notre équipe transmettra votre demande au département concerné.",
			fullName: 'Nom complet', company: "Nom de l'entreprise", email: 'Adresse e-mail professionnelle', country: 'Pays', role: 'Fonction / Poste', type: 'Type de demande', subject: 'Sujet', message: 'Message', phone: 'Numéro de téléphone', services: 'Services concernés', sector: "Secteur d'activité", volume: 'Volume mensuel estimé de vérifications', project: 'Description du projet', choose: 'Choisir…',
			consent: "J'ai pris connaissance de la politique de confidentialité et j'accepte le traitement de mes données pour répondre à ma demande.",
			marketing: 'Je souhaite recevoir des communications d’IZI LENS (facultatif).',
			sensitive: "Ne nous transmettez pas de pièces d'identité ni d'informations sensibles via ce formulaire.",
			submit: 'Envoyer ma demande'
		},
		types: { sales: 'Demande commerciale', demo: 'Demande de démonstration', partnership: 'Partenariat', integration: 'Intégration technologique', institutional: 'Demande institutionnelle', other: 'Autre demande', quote: 'Demande de devis', developer: 'Demande d’accès développeur' },
		services: { kyc: "KYC — Vérification d'identité", kyb: "KYB — Vérification d'entreprise", liveness: 'Biométrie et détection de présence réelle (Liveness)', monitoring: 'Monitoring et suivi', api: 'Intégration API', other: 'Autre' },
		demoForm: { title: 'Demande de démonstration', text: "Présentez-nous votre activité : notre équipe commerciale vous recontactera pour organiser la présentation.", submit: 'Soumettre ma demande de démonstration' },
		institutional: { title: 'IZI LENS', text: "Une solution développée au sein de Kafintech Group Inc.", hq: 'Siège du groupe : Alberta, Canada.' },
		confirm: { title: 'Merci de nous avoir contactés !', text: "Votre demande a bien été reçue par IZI LENS. Notre équipe va l'examiner et la transmettre au département concerné. Nous vous contacterons à l'adresse email indiquée si des informations complémentaires sont nécessaires.", ref: 'Numéro de référence', another: 'Envoyer une autre demande' },
		errors: { required: 'Ce champ est obligatoire.', email: 'Saisissez une adresse e-mail valide.', consent: 'Votre consentement est nécessaire pour envoyer la demande.', server: "Votre demande n'a pas pu être transmise. Veuillez réessayer dans un instant.", spam: 'Soumission refusée.' },
		portal: { title: 'Portail client', text: "Le support technique est accessible aux clients depuis le portail sécurisé." }
	}
};

export default pages;
export type PagesDict = typeof pages;
