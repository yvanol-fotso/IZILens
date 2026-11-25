import type { PagesDict } from './pages.fr';

/** English editorial content of the public site. Must mirror pages.fr.ts exactly (same keys, same shape). */
const pages: PagesDict = {
	nav: {
		home: 'Home',
		services: 'Services',
		solutions: 'Solutions',
		developers: 'Developers',
		resources: 'Resources',
		pricing: 'Pricing',
		about: 'About',
		contact: 'Contact',
		signIn: 'Sign in',
		demo: 'Request a demo',
		menu: 'Menu',
		language: 'Language',
		theme: 'Theme',
		themeLight: 'Light',
		themeDark: 'Dark',
		themeSystem: 'System',
		openApp: 'Open dashboard'
	},
	site: {
		slogan: 'Building trust in every digital interaction.',
		byline: 'by Kafintech Group'
	},
	footer: {
		about: 'IZI LENS is an identity and business verification technology platform developed by Kafintech Group.',
		columns: { platform: 'Platform', developers: 'Developers', company: 'Company', legal: 'Legal information' },
		links: { home: 'Home', services: 'Our services', solutions: 'Solutions', pricing: 'Pricing', developers: 'Developer area', resources: 'Resources', about: 'About', contact: 'Contact', demo: 'Request a demo', signIn: 'Customer sign-in' },
		privacy: 'Privacy Policy',
		terms: 'Terms of Use',
		cookies: 'Cookie Policy',
		cookiePrefs: 'Cookie Preferences',
		copyright: '© {year} IZI LENS – A Kafintech Group Company. All rights reserved.'
	},
	common: {
		quote: 'Request a quote',
		customQuote: 'Get a custom quote',
		demo: 'Request a demo',
		learnMore: 'Learn more',
		discover: 'Discover',
		features: 'Key features',
		useCases: 'Use cases',
		servicesFor: 'Suitable services',
		selected: '{count} service(s) selected',
		planned: 'Planned features',
		comingSoon: 'Coming soon'
	},
	svcNames: {
		kyc: 'KYC — Identity verification',
		kyb: 'KYB — Business verification',
		liveness: 'Liveness & Biometrics — Biometric verification',
		monitoring: 'Monitoring & Tracking — Verification oversight'
	},
	home: {
		hero: {
			title: 'Verify identities. Strengthen digital trust.',
			text1: 'IZI LENS is an international identity and business verification platform designed to help organizations secure their digital interactions.',
			text2: 'With a modular approach combining KYC, KYB, biometrics and monitoring, IZI LENS helps you know your users better, verify your business partners and strengthen your digital trust processes.',
			primary: 'Request a demo',
			secondary: 'Discover our services',
			demoTitle: 'Case KYC-20418',
			demoScan: 'Analysis in progress',
			demoDocument: 'Document authentic',
			demoFace: 'Face match',
			demoLiveness: 'Liveness detected',
			demoRisk: 'Low risk'
		},
		intro: {
			title: 'Digital trust starts with a verified identity.',
			p1: 'In a world where digital interactions keep multiplying, verifying people’s identity and companies’ authenticity has become essential.',
			p2: 'IZI LENS provides a technology platform designed to simplify verification processes, improve how well you know your users and help prevent risks linked to fraudulent identities.',
			p3: 'Whether you are a bank, a fintech, a microfinance institution, an insurance company or a digital business, our solutions help you build a safer, more reliable digital environment.',
			p4: 'Our ambition: make identity verification more accessible, smoother and easier to integrate into digital journeys, everywhere in the world.'
		},
		services: {
			title: 'Modular solutions tailored to your needs.',
			text: 'With IZI LENS, you choose the services that match your organization’s requirements. Activate a single module or combine several solutions to build your verification setup.',
			button: 'Choose my services'
		},
		why: {
			title: 'A platform built for the demands of digital business.',
			items: {
				modular: { title: 'A modular approach', desc: 'Select only the services your organization needs. Combine the solutions according to your processes and requirements.' },
				simple: { title: 'A simplified experience', desc: 'Make your users’ verification journeys easier with an experience designed to limit unnecessary steps.' },
				integrable: { title: 'Integrable technology', desc: 'Connect IZI LENS features to your existing applications and systems through an API-oriented architecture.' },
				visibility: { title: 'Better operational visibility', desc: 'Track verifications, check statuses and access important events from your management tools.' },
				security: { title: 'A security-focused approach', desc: 'Information protection and access control are essential elements of the platform’s design.' },
				international: { title: 'An international ambition', desc: 'Support your activities across different markets with a platform designed for varied digital environments.' }
			}
		},
		how: {
			title: 'From collection to verification, a simplified journey.',
			steps: {
				s1: { title: 'Information collection', desc: 'The user submits the information and documents required for verification.' },
				s2: { title: 'Analysis and verification', desc: 'Planned checks are performed on documents, data and, depending on the journey, biometric elements.' },
				s3: { title: 'Assessment and review', desc: 'Results are processed according to defined rules. Cases requiring intervention can be routed to manual review.' },
				s4: { title: 'Result and follow-up', desc: 'Check the verification status and find the related events from your IZI LENS environment.' }
			}
		},
		sectors: {
			title: 'A solution built for several industries.',
			text: 'IZI LENS supports organizations facing identification, customer knowledge and digital trust challenges.',
			button: 'Explore our industry solutions',
			items: {
				banks: { title: 'Banks and financial institutions', desc: 'Customer identification and business verification.' },
				fintech: { title: 'Fintech and payments', desc: 'User verification and secure digital journeys.' },
				micro: { title: 'Microfinance', desc: 'Customer identification and file verification.' },
				insurance: { title: 'Insurance', desc: 'Verification of policyholders and the information provided.' },
				telecom: { title: 'Telecommunications', desc: 'Subscriber identification and verification.' },
				ecommerce: { title: 'E-commerce and marketplaces', desc: 'Verification of sellers and business partners.' },
				platforms: { title: 'Digital platforms', desc: 'User verification and fraud prevention.' }
			}
		},
		api: {
			title: 'Embed verification directly in your applications.',
			p1: 'With IZI LENS, businesses and technical teams can integrate verification features into their own applications and digital journeys.',
			p2: 'Our API-oriented approach aims to make it easier to connect your IT environment with IZI LENS verification services.',
			p3: 'Whether you are building a fintech app, a payment platform or a customer management system, you can design an integration that fits your architecture.',
			primary: 'Explore our API',
			secondary: 'Access developer documentation'
		},
		security: {
			title: 'Security at the heart of our approach.',
			lead: 'Identity data and business information require particular care.',
			text: 'IZI LENS places great importance on processing security, access management, traceability of operations and protection of the information handled by the platform.',
			intro: 'Our approach is notably based on:',
			points: [
				'Controlled management of access and permissions.',
				'Protection of information and documents.',
				'Traceability of sensitive operations.',
				'Separation of technical environments.',
				'Consideration of applicable data protection requirements.'
			],
			closing: 'Digital trust starts with responsible data management.'
		},
		pricing: {
			title: 'Flexible pricing, adapted to your organization.',
			p1: 'Every organization has different needs, volumes and requirements.',
			p2: 'IZI LENS offers a flexible pricing approach that lets you select the services you need and choose a plan suited to your activity.',
			p3: 'Depending on your needs, you will be able to access structured offers or request a custom commercial proposal.',
			intro: 'Our pricing approach:',
			points: [
				'Services available individually.',
				'Plans combining several services.',
				'Pricing adapted to verification volumes.',
				'Custom commercial proposals.',
				'Ability to study specific integration needs.'
			],
			primary: 'View our pricing',
			secondary: 'Get a custom offer'
		},
		cta: {
			title: 'Ready to strengthen trust in your digital operations?',
			p1: 'Find out how IZI LENS can support your organization in its identity and business verification processes.',
			p2: 'Tell us about your activity, your needs and the services you are interested in. Our team can offer a demo tailored to your organization.',
			primary: 'Request a demo',
			secondary: 'Configure my offer'
		}
	},
	svc: {
		hero: {
			kicker: 'The right verification solutions for your business.',
			title: 'Our services',
			text1: 'IZI LENS offers a suite of identity and business verification solutions designed to help organizations build trust in their digital interactions.',
			text2: 'From verifying individuals to identifying companies, including biometrics and verification tracking, our services adapt to your business needs.',
			primary: 'Discover our solutions',
			secondary: 'Request a quote'
		},
		overview: {
			title: 'Solutions adapted to your verification requirements',
			text: 'Every company has its own identification, security and verification requirements. IZI LENS lets you freely select the services you need and build a solution tailored to your organization.',
			mainTitle: 'Our four main services',
			note: 'Each service has its own detailed page with its features, use cases and integration options.'
		},
		items: {
			kyc: {
				code: 'KYC', name: 'Know Your Customer',
				short: 'Verification of individuals’ identity through the collection and analysis of identity information and documents.',
				title: 'Identity verification',
				tagline: 'Verify your users’ identity and simplify your digital onboarding.',
				intro: 'IZI LENS KYC lets businesses collect and review their customers’ identity information through a structured process.',
				problem: 'Onboarding users quickly without multiplying steps, while keeping control over the information and documents collected.',
				features: [
					'Collection of personal information.', 'Upload or capture of identity documents.', 'Document quality and legibility checks.',
					'Information extraction through optical character recognition (OCR), where available.', 'Consistency checks on collected data.', 'Verification status management.',
					'Requests for corrections or additional information.', 'Option of manual case review.'
				],
				useCases: ['Opening digital accounts.', 'Registration on financial platforms.', 'Fintech user onboarding.', 'Customer identification for microfinance institutions.', 'Verification of digital platform users.'],
				benefits: ['A smoother onboarding journey.', 'Structured cases with viewable statuses and history.', 'Manual review for uncertain cases.'],
				faq: [
					{ q: 'What happens if a document is unreadable?', a: 'The quality check flags it, and a correction or additional information can be requested.' },
					{ q: 'Is a human decision possible?', a: 'Yes. Cases requiring intervention can be routed to manual review.' }
				],
				cta: 'Discover the KYC service'
			},
			kyb: {
				code: 'KYB', name: 'Know Your Business',
				short: 'Verification of companies, their legal documents, their representatives and their beneficial owners.',
				title: 'Business verification',
				tagline: 'Know the companies you enter business or financial relationships with.',
				intro: 'IZI LENS KYB helps structure the verification of companies, their legal documents and the people who represent them.',
				problem: 'Knowing precisely who is behind a company: legal documents, directors and beneficial owners.',
				features: [
					'Collection of company information.', 'Collection and review of legal documents.', 'Identification of directors and legal representatives.', 'Identification of beneficial owners (UBO).',
					'Viewing of the declared ownership structure.', 'Identification of missing information.', 'Management of requests for additional items.', 'Verification history and tracking.'
				],
				useCases: ['Onboarding business customers.', 'Opening business accounts.', 'Verification of merchants and sellers.', 'Onboarding suppliers and partners.', 'Verification of business customers of financial platforms.'],
				benefits: ['A clear view of the people linked to the company.', 'Missing information identified from the start.', 'Complete verification history.'],
				faq: [
					{ q: 'What is examined?', a: 'Company information, legal documents, representatives and beneficial owners (UBO), according to the agreed scope.' },
					{ q: 'Can additional items be requested?', a: 'Yes, managing requests for additional items is part of the service.' }
				],
				cta: 'Discover the KYB service'
			},
			liveness: {
				code: 'Liveness & Biometrics', name: 'Biometrics and liveness detection',
				short: 'Biometric verification and liveness checks to strengthen the reliability of identification processes.',
				title: 'Biometrics and liveness detection',
				tagline: 'Strengthen the reliability of your identity verifications.',
				intro: 'This service adds a biometric step to the verification process, helping confirm that the person presented matches the submitted identity and is really present during the check, depending on the features enabled.',
				problem: 'Making sure the person behind the screen is the one on the document, and that they are present live.',
				features: [
					'Face image capture.', 'Image quality control.', 'Liveness verification.', 'Face comparison where this feature is available and enabled.',
					'Checks against certain presentation attacks.', 'Delivery of available results or scores.', 'Option of additional review when a result is uncertain.'
				],
				useCases: ['Remote user verification.', 'Opening financial accounts.', 'Strong authentication.', 'Validation of sensitive operations.', 'Identification journeys requiring a biometric check.'],
				benefits: ['Greater reliability of remote verifications.', 'Results and scores available in the case.', 'Additional review when in doubt.'],
				faq: [
					{ q: 'Is face comparison always active?', a: 'It is offered where the feature is available and enabled for your organization.' },
					{ q: 'What if the result is uncertain?', a: 'An additional review can be triggered.' }
				],
				cta: 'Discover Liveness & Biometrics'
			},
			monitoring: {
				code: 'Monitoring & Tracking', name: 'Verification oversight',
				short: 'Tracking of verification requests, status checks, event history and operational alert management.',
				title: 'Verification oversight',
				tagline: 'Keep visibility over your verification processes.',
				intro: 'IZI LENS Monitoring lets organizations track their verification requests and view their progress through an oversight interface.',
				problem: 'Knowing where each case stands, spotting blocked ones and keeping a trace of the actions taken.',
				features: [
					'Tracking of verification requests.', 'Status viewing: pending, in progress, approved, rejected or requiring intervention.', 'Event history.', 'Traceability of actions performed.',
					'Operational alerts.', 'Identification of pending cases.', 'Search and filtering of requests.', 'Viewing of results and how they evolve.'
				],
				useCases: ['Oversight of KYC and KYB operations.', 'Tracking customer cases.', 'Managing pending verifications.', 'Operational control of identification processes.', 'Viewing verification history.'],
				benefits: ['End-to-end operational visibility.', 'Pending cases identified quickly.', 'Viewable history and traceability.'],
				faq: [
					{ q: 'Does Monitoring watch financial transactions?', a: 'No. It covers functional tracking of verification requests and is not, on its own, a transaction monitoring or money-laundering detection engine.' },
					{ q: 'Can requests be filtered?', a: 'Yes, search and filtering of requests are planned.' }
				],
				note: 'Important: the Monitoring service described here covers functional tracking of verification requests. On its own, it is not a complete engine for monitoring financial transactions or detecting money-laundering operations.',
				cta: 'Discover Monitoring & Tracking'
			}
		},
		detail: { problem: 'The challenge', benefits: 'Benefits for businesses', integration: 'Integration options', faq: 'Frequently asked questions', back: 'All services', integrationText: 'Depending on available features and the agreed scope: APIs, SDKs where available, Webhooks for events and configurable verification workflows.' },
		compose: { title: 'You choose. We adapt the solution.', text: 'With IZI LENS you do not have to subscribe to every service. Select only the modules matching your operational needs.', button: 'Request a custom quote' },
		sectors: { title: 'Solutions for several industries', text: 'IZI LENS supports organizations that want to build reliable verification and identification processes into their activities.', note: 'The services can be combined according to each industry’s requirements and each organization’s needs.' },
		integration: {
			title: 'Integrate IZI LENS into your digital environment.',
			text: 'Our solutions are designed to integrate with companies’ systems and applications through suitable technical interfaces.',
			intro: 'Depending on available features and the agreed scope, integration can notably rely on:',
			list: ['APIs.', 'SDKs, where available.', 'Webhooks for event delivery.', 'Configurable verification workflows.'],
			primary: 'Explore our API', secondary: 'Contact our technical team'
		},
		pricing: {
			title: 'An offer adapted to your organization.',
			text: 'Every company has different volumes, constraints and needs. IZI LENS offers a custom pricing approach to build an offer matching your usage.',
			intro: 'Pricing is set by quote, based notably on:',
			list: ['The services selected.', 'The expected volume of verifications.', 'The countries and markets concerned.', 'The features requested.', 'Technical integration needs.', 'The level of support desired.']
		},
		final: { title: 'Let’s build your verification solution together.', text: 'Whether you want to verify individuals, identify companies, strengthen your biometric checks or oversee your verification processes, IZI LENS supports you in setting up a suitable solution.' }
	},
	sol: {
		hero: {
			kicker: 'Verification solutions built around your business.',
			title: 'Verification solutions adapted to your industry, anywhere in the world.',
			text1: 'Every organization has its own identification, verification and digital trust requirements.',
			text2: 'IZI LENS supports businesses and institutions worldwide with modular solutions to verify individuals and companies, strengthen biometric checks and oversee verification processes.',
			primary: 'Explore our solutions', secondary: 'Request a demo'
		},
		intro: {
			title: 'One platform. Several industries. An international approach.',
			p1: 'IZI LENS gives organizations a suite of services designed to meet the verification and identification needs of different industries.',
			p2: 'Our platform is aimed notably at financial institutions, fintechs, payment companies, insurers, telecom operators and digital platforms.',
			p3: 'Thanks to its modular architecture, each organization can freely select the services matching its needs.',
			modulesTitle: 'Our four modules:',
			modules: ['KYC — Verification of individuals.', 'KYB — Verification of businesses.', 'Liveness & Biometrics — Biometric verification and liveness.', 'Monitoring — Tracking and oversight of verifications.']
		},
		sectorsTitle: 'Solutions by industry',
		needs: 'Needs covered',
		sectors: {
			banks: { name: 'Banks and financial institutions', tagline: 'Strengthen your customer identification and onboarding processes.', desc: 'Financial institutions must be able to identify their customers, collect the necessary information and organize their verification processes. IZI LENS helps structure these steps through journeys adapted to each institution’s operational requirements.', needs: ['Verification of individual customers’ identity.', 'Verification of business customers.', 'Additional biometric checks.', 'Tracking of verification requests.', 'Viewing of check history.'] },
			fintech: { name: 'Fintechs and payment companies', tagline: 'Simplify user onboarding and structure your verifications.', desc: 'Fintechs and payment companies need digital sign-up journeys adapted to their users and to the markets they operate in. IZI LENS lets them integrate verification steps into their applications and platforms.', needs: ['Identification of new users.', 'Collection and verification of documents.', 'Biometric verification depending on the chosen journey.', 'Identification of partner or merchant companies.', 'Tracking of requests and their statuses.', 'Integration with existing systems.'] },
			micro: { name: 'Microfinance institutions', tagline: 'Structure the identification of your customers and partners.', desc: 'Microfinance institutions serve individuals, entrepreneurs and organizations with varied profiles. IZI LENS helps set up structured verification processes to support their digital transformation.', needs: ['Identification of individual customers.', 'Verification of identity documents.', 'Verification of business and organization customers.', 'Additional biometric checks.', 'Tracking of verification cases.', 'Viewing of check history.'] },
			insurance: { name: 'Insurance companies', tagline: 'Strengthen the reliability of your identification journeys.', desc: 'Insurance companies can use IZI LENS to structure the identification steps for their policyholders, intermediaries and partners.', needs: ['Verification of policyholders’ identity.', 'Verification of representatives and professional partners.', 'Biometric checks as needed.', 'Tracking of verification requests.', 'Traceability of case-related events.'] },
			telecom: { name: 'Telecommunications', tagline: 'Support your digital identification journeys.', desc: 'Telecom operators and digital service providers can integrate verification processes to structure the identification of their users and partners.', needs: ['Verification of individual identities.', 'Collection and review of documents.', 'Verification of partner companies.', 'Additional biometric checks.', 'Tracking of verification requests.'] },
			ecommerce: { name: 'E-commerce and marketplaces', tagline: 'Build a more trustworthy digital environment for your users and sellers.', desc: 'Online commerce platforms may need to verify different profiles: buyers, professional sellers, merchants and partners. IZI LENS helps set up journeys adapted to these profiles.', needs: ['Verification of users.', 'Verification of professional sellers and merchants.', 'Identification of company representatives.', 'Biometric checks depending on the desired verification level.', 'Tracking of cases and results.'] },
			platforms: { name: 'Digital platforms and technology companies', tagline: 'Embed verification directly in your digital journeys.', desc: 'Companies building applications and online services can integrate IZI LENS features into their own environments.', needs: ['Remote user verification.', 'Verification of business accounts.', 'Integration of biometric checks.', 'Automation of certain steps according to configured workflows.', 'Tracking of requests and viewing of results.', 'Connection to existing systems via API.'] }
		},
		modular: { title: 'You choose the services your business needs.', text: 'IZI LENS does not impose a single plan. You can select one service or combine several modules according to your activities and operational requirements.', hint: 'You can start with one service and evolve your setup as your needs grow.', button: 'Compose my solution' },
		intl: { kicker: 'Building trust across borders.', title: 'An internationally oriented platform', p1: 'Organizations operate in increasingly international environments. Their customers, partners and users may be located in different countries.', p2: 'IZI LENS is designed to support businesses operating in several markets, with a modular approach and integration options adapted to their digital environments.', p3: 'Our ambition is to make it easier to set up consistent verification processes in different geographic contexts.', primary: 'Discover our services', secondary: 'Contact our team' },
		tech: { title: 'Connect IZI LENS to your digital environment.', text: 'IZI LENS is designed to integrate with organizations’ applications and systems.', intro: 'Depending on available features and the technical scope chosen, integration options may include:', list: ['APIs to connect verification features.', 'SDKs, when available, to ease integration.', 'Webhooks to receive verification-related events.', 'Workflows configurable according to the chosen journeys.'], note: 'Our team can support the study of your integration needs.', primary: 'Explore our developer documentation', secondary: 'Talk to our technical team' },
		why: { title: 'An approach built for modern organizations.', items: { modularity: { title: 'Modularity', desc: 'Select the services matching your needs.' }, adaptability: { title: 'Adaptability', desc: 'Build verification journeys adapted to your industry.' }, integration: { title: 'Integration', desc: 'Connect features to your existing applications and systems.' }, visibility: { title: 'Operational visibility', desc: 'Follow the progress of your verification requests.' }, reach: { title: 'International reach', desc: 'A platform designed to support organizations operating in different markets.' } } },
		final: { title: 'Your business deserves a suitable verification solution.', text: 'Whether you are a bank, a fintech, a microfinance institution, an insurance company or a digital platform, IZI LENS helps you build a solution adapted to your operational and technical requirements.' }
	},
	dev: {
		hero: { kicker: 'Powerful verification APIs. Seamless integration.', title: 'Integrate identity and business verification directly into your applications.', text1: 'IZI LENS gives developers and businesses a technical environment designed to connect KYC, KYB, Liveness & Biometrics and Monitoring features to their own applications and systems.', text2: 'With our programming interfaces and integration tools, build verification journeys adapted to your technical environment.', primary: 'Request developer access', secondary: 'Sign in' },
		intro: { title: 'Everything you need to integrate digital verification.', text: 'Whether you are building a financial application, a payment platform, a digital service or an internal system, IZI LENS lets you connect verification features to your existing infrastructure.', intro: 'The developer environment is organized around several components:', list: ['Verification APIs.', 'SDKs, depending on supported languages and environments.', 'Webhooks for receiving events.', 'Secure technical documentation.', 'Sandbox environment for testing.', 'Production environment for real operations.', 'Management of API access and credentials.'] },
		apisTitle: 'Our API interfaces',
		apis: {
			kyc: { name: 'KYC API', tag: 'Identity Verification', desc: 'Integrate verification of individuals into your applications.', list: ['Creation of a KYC verification request.', 'Transmission of identity information.', 'Document submission.', 'Checking the status of a verification.', 'Retrieval of available results.', 'Management of requests requiring intervention.'] },
			kyb: { name: 'KYB API', tag: 'Business Verification', desc: 'Connect business verification features to your systems.', list: ['Creation of a KYB request.', 'Transmission of company information.', 'Submission of legal documents.', 'Management of directors and representatives.', 'Collection of beneficial owner (UBO) information.', 'Checking available statuses and results.'] },
			bio: { name: 'Liveness & Biometrics API', tag: 'Biometrics', desc: 'Add biometric checks to your verification journeys.', list: ['Initialization of a biometric session.', 'Capture of the data needed for the check.', 'Liveness verification.', 'Face comparison where available.', 'Checking verification results and information.'] },
			mon: { name: 'Monitoring API', tag: 'Monitoring', desc: 'Connect verification tracking information to your internal tools.', list: ['Checking request statuses.', 'Following the progress of verifications.', 'Viewing available events.', 'Access to authorized tracking information.', 'Integration of events into internal systems.'] }
		},
		publishRule: 'Only features that are actually developed, tested and validated are presented as operational. The features listed above are planned and will be opened progressively.',
		sdk: { title: 'SDKs and integration tools', text: 'IZI LENS aims to make it easier to integrate its services in different development environments. SDKs will simplify certain integration and API communication tasks.', note: 'Languages and environments will be displayed based on the SDKs actually developed and published.' },
		webhooks: { title: 'Webhooks', text: 'Webhooks let your application receive notifications when a verification-related event occurs. They help automate internal processes and keep IZI LENS and your systems in sync.', eventsTitle: 'Example events', events: ['Verification request created.', 'Verification started.', 'Document submitted.', 'Verification completed.', 'Result available.', 'Verification requiring intervention.'] },
		docs: { title: 'Technical documentation', text: 'The full technical documentation is intended for developers and integration teams. It is available only to users with a developer account who are signed in.', topics: ['Getting Started', 'Authentication', 'KYC API', 'KYB API', 'Biometrics API', 'Monitoring API', 'Webhooks', 'Errors & Responses'] },
		access: {
			title: 'API access process',
			steps: { s1: { title: 'Create an account', desc: 'The developer or company fills in the registration form and provides the requested information.' }, s2: { title: 'Sign in to the developer area', desc: 'After creating their account, the user accesses their secure area and the technical documentation.' }, s3: { title: 'Request API access', desc: 'The user specifies their organization, integration project, desired services (KYC, KYB, Biometrics or Monitoring), intended use and the technical information needed.' }, s4: { title: 'Validation and activation', desc: 'The IZI LENS team reviews the request. After approval, authorized API access is activated and the matching credentials are made available in the developer area.' } },
			note: 'Creating an account therefore does not mean production API access is automatically activated.'
		},
		env: { title: 'Develop, test and deploy with confidence.', sandbox: { name: 'Sandbox — Test environment', desc: 'Lets you test your integrations without performing real operational verifications.', list: ['API connection tests.', 'Simulation of verification journeys.', 'Use of test data.', 'Webhook tests.', 'Simulation of responses and statuses.'] }, prod: { name: 'Production — Operational environment', desc: 'Lets you use IZI LENS services in an operational context, after access validation.', list: ['Use of production credentials.', 'Submission of real requests.', 'Viewing of results according to permissions.', 'Receipt of operational events.', 'Tracking of verification requests.'] }, note: 'Sandbox and Production credentials and data are distinct and separated.' },
		security: { title: 'Security is part of the integration.', list: ['Authentication of API requests.', 'Protection and management of API keys.', 'Secure communication between systems.', 'Permission control.', 'Logging of technical events.', 'Separation of test and production environments.', 'Administrator access with multi-factor authentication (MFA): TOTP and passkeys, depending on the scope chosen.'] },
		support: { title: 'Need support?', text: 'Do you have a specific integration project? Our team can talk with your developers to understand your technical needs and identify the right integration approach.', primary: 'Request developer access', secondary: 'Contact our technical team' }
	},
	res: {
		hero: { title: 'Explore the IZI LENS Resource Center', subtitle: 'Insights, guides and resources to help you build secure digital experiences and strengthen trust.' },
		searchLabel: 'Search resources', searchPlaceholder: 'Search a question, a guide, a topic…',
		rubriques: {
			blog: { title: 'Blog & News', desc: 'Articles written by IZI LENS and selected external news, with attribution and a link to the source.', items: ['KYC & Identity Verification', 'KYB & Business Verification', 'Biometrics & Liveness', 'AML & Compliance', 'Fraud Prevention', 'Fintech & Digital Identity', 'Digital Trust & Security'] },
			guides: { title: 'Guides & E-books', desc: 'Free guides with direct access; premium content after a short professional form.', items: ['The Complete Guide to KYC Verification', 'Understanding KYB and Business Verification', 'Biometrics and Liveness Detection Explained', 'How to Build a Digital Identity Verification Process', 'Fraud Prevention in Digital Financial Services', 'KYC Compliance for Fintech Companies'] },
			api: { title: 'Documentation & API Resources', desc: 'Public introductory resources. The full technical documentation stays private, after creating a developer account and access validation.', items: ['Overview of IZI LENS APIs', 'Introduction to integration', 'Introductory technical guides', 'Integration examples', 'Available Webhooks', 'Sandbox and Production environments'] },
			cases: { title: 'Case Studies & Use Cases', desc: 'Illustrative industry scenarios. No customer testimonial or result is published without authorization and proof.', items: ['Banks and financial institutions', 'Fintech and payment companies', 'Microfinance institutions', 'Insurance', 'Telecommunications', 'E-commerce and marketplaces', 'Digital platforms'] },
			security: { title: 'Security & Compliance Resources', desc: 'Resources on security and digital trust. No certification is presented as obtained until it is actually obtained and verified.', items: ['Data Protection', 'Identity Verification Security', 'Document Verification', 'Biometric Security', 'Fraud Prevention', 'Compliance Resources', 'Privacy & Data Governance'] }
		},
		soon: 'First content coming soon',
		faq: { title: 'Frequently asked questions', empty: 'No question matches your search.', categories: { general: 'General', kyc: 'KYC', kyb: 'KYB', bio: 'Biometrics & Liveness', api: 'API & integration' }, items: [
			{ c: 'general', q: 'What is IZI LENS?', a: 'IZI LENS is a modular international identity and business verification platform: KYC, KYB, biometrics and monitoring.' },
			{ c: 'kyc', q: 'What is KYC verification?', a: 'KYC (Know Your Customer) consists of collecting, analyzing and verifying a person’s identity information and documents.' },
			{ c: 'kyb', q: 'What is the difference between KYC and KYB?', a: 'KYC verifies individuals; KYB verifies companies, their legal documents, their representatives and their beneficial owners.' },
			{ c: 'bio', q: 'How does biometric verification work?', a: 'It adds a face capture, a liveness check and, where the feature is enabled, a face comparison with the document.' },
			{ c: 'general', q: 'How can I request a demo?', a: 'Use the “Request a demo” button: our sales team reviews your request and contacts you.' },
			{ c: 'api', q: 'How do I access the API?', a: 'Create a developer account, then submit an access request. Access is activated after validation by the IZI LENS team.' }
		] },
		dev: { title: 'For developers', text: 'Discover the technical environment and request access to the secure developer portal.', primary: 'Access the developer portal' },
		cta: { title: 'A question about identity verification?', primary: 'Request a demo', secondary: 'Contact our team' }
	},
	about: {
		hero: { kicker: 'Our Story', title: 'From a Canadian vision to an international technology ecosystem' },
		story: [
			'Founded in Canada, Kafintech Group Inc. is a diversified group developing initiatives in technology, financial services, digital payments and media.',
			'Since its creation, the group has pursued one ambition: to design and develop innovative solutions able to meet the new needs of businesses, individuals and markets undergoing digital transformation.',
			'As it grew, Kafintech Group gradually extended its activities beyond the Canadian market, notably to several African markets, through different brands, companies and specialized initiatives.',
			'This evolution has built an ecosystem of complementary activities in international transfers, payment solutions, microfinance, financial technology, point-of-sale systems and media.',
			'IZI LENS was developed in this spirit of diversification and innovation: a platform specialized in digital identity verification, KYC, KYB, biometrics and digital trust technologies.',
			'Today, Kafintech Group continues its development with an international ambition: to build a technology and financial ecosystem able to support the transformations of the digital economy.'
		],
		eco: { kicker: 'Our Ecosystem', title: 'A diverse ecosystem. One shared vision.', text: 'Kafintech Group develops several complementary brands and initiatives across different sectors.', items: [
			{ n: 'IZI LIFE PAY', d: 'International money transfer and digital payment solutions.' },
			{ n: 'IZI TRUST CAPITAL', d: 'Microfinance, savings and financing activities.' },
			{ n: 'IZI FLOW', d: 'Payment solution aggregation and integration infrastructure.' },
			{ n: 'IZI ONE', d: 'Point-of-sale solutions and payment management tools.' },
			{ n: 'IZI LENS', d: 'Digital identity verification, KYC, KYB and digital trust platform.' },
			{ n: 'IZI VOXES', d: 'Media, communication and content production.' },
			{ n: 'DIASPO ECO', d: 'Magazine dedicated to entrepreneurship and the diaspora economy.' },
			{ n: 'KAFINTECH — AFRICAN MARKETS', d: 'Development of activities and representations in several African markets, notably Benin, Burkina Faso, Côte d’Ivoire, Togo and the Democratic Republic of the Congo.' }
		] },
		leadership: { kicker: 'Our Leadership', title: 'Experienced teams. Shared ambition.', text: 'Kafintech Group’s growth relies on multidisciplinary teams committed to technology development, financial management, operations, compliance and business development.', intro: 'The institutional presentation of the leadership team will highlight the following responsibilities:', roles: ['Administrative and financial management.', 'Technical management.', 'Commercial management.', 'Strategic advisory.'], note: 'The names, official titles, biographies and portraits of the leaders authorized to be presented will be added to this section.' },
		ambition: { kicker: 'Our Global Ambition', title: 'Developed in Canada. Designed for global markets.', p1: 'From its Canadian base, Kafintech Group pursues a development strategy focused on international markets.', p2: 'The group intends to build scalable technology and financial solutions able to meet the needs of different sectors and contribute to a more accessible, connected and reliable digital economy.' }
	},
	contact: {
		hero: { title: 'Let’s talk about your project.', text: 'Want to discover IZI LENS, integrate our identity verification solutions or discuss a partnership? Our team is available to study your needs.', primary: 'Contact our team', secondary: 'Request a demo' },
		cardsTitle: 'Our contacts',
		cards: {
			sales: { title: 'Sales', tag: 'Sales', desc: 'For companies that want to discover our services, get a commercial proposal or discuss their KYC, KYB, biometrics and monitoring needs.', cta: 'Write to sales' },
			partners: { title: 'Partnerships', tag: 'Partnerships', desc: 'For technology providers, financial institutions, distributors and organizations interested in collaborating with IZI LENS.', cta: 'Propose a partnership' },
			demo: { title: 'Demo', tag: 'Request a Demo', desc: 'Prospects can request a personalized presentation of the platform. The sales team reviews the request and arranges a call if needed.', cta: 'Request a demo' },
			support: { title: 'Technical support', tag: 'Technical Support', desc: 'Technical support is reserved for customers with an IZI LENS account. Access is exclusively through the secure customer portal: submit requests, report an incident and follow your tickets.', cta: 'Access the customer portal' }
		},
		form: {
			title: 'Send us your request.', text: 'Fill in the form below. Our team will forward your request to the relevant department.',
			fullName: 'Full name', company: 'Company name', email: 'Business email address', country: 'Country', role: 'Job title', type: 'Request type', subject: 'Subject', message: 'Message', phone: 'Phone number', services: 'Services concerned', sector: 'Industry', volume: 'Estimated monthly verification volume', project: 'Project description', choose: 'Choose…',
			consent: 'I have read the privacy policy and agree to the processing of my data to answer my request.',
			marketing: 'I would like to receive communications from IZI LENS (optional).',
			sensitive: 'Please do not send identity documents or sensitive information through this form.',
			submit: 'Send my request'
		},
		types: { sales: 'Sales inquiry', demo: 'Demo request', partnership: 'Partnership', integration: 'Technology integration', institutional: 'Institutional request', other: 'Other request', quote: 'Quote request', developer: 'Developer access request' },
		services: { kyc: 'KYC — Identity verification', kyb: 'KYB — Business verification', liveness: 'Biometrics and liveness detection (Liveness)', monitoring: 'Monitoring and tracking', api: 'API integration', other: 'Other' },
		demoForm: { title: 'Demo request', text: 'Tell us about your activity: our sales team will get back to you to arrange the presentation.', submit: 'Submit my demo request' },
		institutional: { title: 'IZI LENS', text: 'A solution developed within Kafintech Group Inc.', hq: 'Group headquarters: Alberta, Canada.' },
		confirm: { title: 'Thank you for contacting us!', text: 'Your request has been received by IZI LENS. Our team will review it and forward it to the relevant department. We will contact you at the email address provided if more information is needed.', ref: 'Reference number', another: 'Send another request' },
		errors: { required: 'This field is required.', email: 'Enter a valid email address.', consent: 'Your consent is required to send the request.', server: 'Your request could not be sent. Please try again in a moment.', spam: 'Submission refused.' },
		portal: { title: 'Customer portal', text: 'Technical support is available to customers from the secure portal.' }
	},
	marketing: {
		pricing: {
			title: 'Simple and transparent pricing',
			subtitle: 'Choose the plan that fits your identity verification needs.',
			faq: 'Frequently asked questions',
			faqBilling: 'Billing is calculated at the end of the month based on your actual consumption (KYC, KYB, Biometrics).',
			faqTaxes: 'Prices shown are exclusive of tax. Currency conversion is indicative.',
			popular: 'Popular',
			start: 'Get started',
			contact: 'Contact us',
			perMonth: 'month',
			perYear: 'year',
			included: 'included',
			ctaTitle: 'Ready to secure your verifications?',
			ctaText: 'Create your account in 2 minutes and test the platform today.'
		}
	}
};

export default pages;