import type { Dictionary } from './fr';

const en: Dictionary = {
	meta: {
		siteTitle: 'IZI LENS — Verify identities, build digital trust',
		siteDescription:
			'Identity verification and compliance infrastructure: documents, biometrics, risk and AML in one modular platform.',
		app: 'Dashboard'
	},
	common: {
		save: 'Save',
		cancel: 'Cancel',
		delete: 'Delete',
		edit: 'Edit',
		create: 'Create',
		search: 'Search',
		loading: 'Loading…',
		back: 'Back',
		next: 'Next',
		previous: 'Previous',
		actions: 'Actions',
		details: 'Details',
		copy: 'Copy',
		copied: 'Copied',
		all: 'All',
		none: 'None',
		close: 'Close',
		confirm: 'Confirm',
		optional: 'optional',
		refresh: 'Refresh',
		view: 'View',
		filter: 'Filter',
		reset: 'Reset',
		learnMore: 'Learn more',
		page: 'Page {page} of {pages}',
		results: '{count} result(s)',
		noData: 'No data',
		unknown: 'Unknown',
		never: 'Never',
		yes: 'Yes',
		no: 'No',
		active: 'Active',
		inactive: 'Inactive',
		name: 'Name',
		date: 'Date',
		email: 'Email',
		role: 'Role',
		organization: 'Organization',
		skipToContent: 'Skip to content'
	},
	nav: {
		platform: 'Platform',
		solutions: 'Solutions',
		coverage: 'Coverage',
		why: 'Why IZI LENS',
		industries: 'Industries',
		resources: 'Resources',
		company: 'Company',
		developers: 'Developers',
		signIn: 'Sign in',
		getStarted: 'Get started',
		contactSales: 'Contact sales',
		openApp: 'Open dashboard',
		menu: 'Menu',
		language: 'Language',
		theme: 'Theme',
		themeLight: 'Light',
		themeDark: 'Dark',
		themeSystem: 'System'
	},
	solutions: {
		groups: {
			verification: 'Verification',
			compliance: 'Compliance',
			platform: 'Platform'
		},
		items: {
			identity: 'Identity verification',
			document: 'Document verification',
			biometric: 'Biometric verification',
			liveness: 'Liveness detection',
			aml: 'AML screening',
			sanctions: 'Sanctions screening',
			pep: 'PEP screening',
			media: 'Adverse media check',
			api: 'API integration',
			analytics: 'Dashboard & analytics',
			security: 'Security & privacy',
			coverage: 'Global coverage'
		}
	},
	home: {
		hero: {
			title: 'Know who is at the door before they come in.',
			subtitle:
				'Documents, biometrics, risk and compliance: one infrastructure to know who you are dealing with, in seconds and without friction for your customers.',
			primary: 'Talk to our team',
			secondary: 'Explore the API',
			demoTitle: 'Case KYC-20418',
			demoDocument: 'Document authentic',
			demoFace: 'Face match',
			demoLiveness: 'Liveness detected',
			demoRisk: 'Low risk',
			demoScan: 'Analysis in progress'
		},
		platform: {
			title: 'A complete journey, from document to decision',
			subtitle:
				'Each step works alone or as part of a chain. Turn on only the modules your organization needs.',
			steps: {
				collect: { title: 'Collect', desc: 'Capture and validate documents and data.' },
				verify: { title: 'Verify', desc: 'Authenticate identities with advanced checks.' },
				assess: { title: 'Assess', desc: 'Detect risks and suspicious activity.' },
				act: { title: 'Decide', desc: 'Apply configurable rules and workflows.' },
				integrate: { title: 'Integrate', desc: 'Embed verification with our APIs and SDKs.' }
			}
		},
		coverage: {
			title: 'Verify users across the globe',
			subtitle:
				'Onboard individuals and businesses in multiple countries, with a wide range of identity documents and respect for local regulations.',
			stats: {
				countries: { value: '200+', label: 'Countries & territories' },
				docs: { value: '5,000+', label: 'Identity document types' },
				compliance: { value: 'Global', label: 'Compliance support' },
				speed: { value: 'Fast', label: 'Verification in seconds' }
			},
			docs: {
				passports: { title: 'Passports', desc: 'Passports from all major countries.' },
				ids: { title: 'National IDs', desc: 'Government-issued identity cards.' },
				licenses: { title: "Driver's licenses", desc: 'Local and international licenses.' },
				permits: { title: 'Residence permits', desc: 'Permits and residence cards.' },
				business: { title: 'Business documents', desc: 'Company documents and beneficial owners.' }
			}
		},
		why: {
			title: 'Safer, smarter and simpler',
			subtitle:
				'Advanced technology, global coverage and a seamless experience to verify users, reduce fraud and accelerate your growth.',
			items: {
				fraud: { title: 'Advanced fraud prevention', desc: 'AI-powered checks to detect and stop fraudulent activity.' },
				coverage: { title: 'Global coverage', desc: 'Verify users and businesses in multiple countries.' },
				speed: { title: 'Fast, seamless experience', desc: 'Verify users in seconds with a smooth process.' },
				flexible: { title: 'Flexible and scalable', desc: 'Easily integrate and adapt to your business needs.' },
				compliance: { title: 'Built for compliance', desc: 'Stay compliant with local regulations and global standards.' }
			}
		},
		cta: {
			title: 'Ready to verify with confidence?',
			subtitle:
				'Join organizations that trust IZI LENS to verify users, prevent fraud and stay compliant.',
			primary: 'Talk to our team',
			secondary: 'View API documentation',
			perks: {
				onboarding: { title: 'Fast onboarding', desc: 'Get started quickly with our team’s support.' },
				integration: { title: 'Flexible integration', desc: 'Via our API or simple tools.' },
				support: { title: 'Dedicated support', desc: 'Our experts help you at every step.' },
				partner: { title: 'A long-term partner', desc: 'Grow with a reliable partner.' }
			}
		}
	},
	footer: {
		tagline:
			'IZI LENS helps businesses verify identities, assess risk, and build safer digital experiences through configurable verification workflows.',
		columns: {
			solutions: 'Solutions',
			industries: 'Industries',
			developers: 'Developers',
			company: 'Company',
			legal: 'Legal & Privacy',
			contact: 'Contact',
			social: 'Social'
		},
		solutions: {
			identity: 'Identity Verification',
			biometric: 'Biometric Verification',
			kyb: 'Business Verification (KYB)',
			aml: 'AML & Risk Screening',
			fraud: 'Fraud Prevention',
			coverage: 'Global Coverage'
		},
		industries: {
			financial: 'Financial Services',
			fintech: 'Fintech',
			ecommerce: 'E-commerce & Marketplaces',
			crypto: 'Crypto & Digital Assets',
			mobility: 'Mobility',
			platforms: 'Online Platforms'
		},
		links: { docs: 'API Documentation', signIn: 'Dashboard sign-in', contact: 'Contact' },
		privacy: 'Privacy Policy',
		terms: 'Terms of Use',
		cookies: 'Cookie Policy',
		cookiePrefs: 'Cookie Preferences',
		rights: 'All rights reserved.',
		language: 'Language'
	},
	cookieBanner: {
		title: 'Cookies and similar technologies',
		text: 'We use cookies and similar technologies to keep this website working, remember your preferences, understand website usage, and support optional features. You can accept optional cookies, reject them, or customise your choices.',
		acceptAll: 'Accept all',
		rejectAll: 'Reject optional cookies',
		customize: 'Customise',
		preferences: 'Cookie preferences',
		preferencesText: 'Choose which optional categories you allow. You can change or withdraw your consent at any time.',
		save: 'Save my preferences',
		alwaysActive: 'Always active',
		version: 'Version {version} · effective {date}',
		necessary: { title: 'Strictly necessary', desc: 'Required for core site functions, security, and storing your consent choices.' },
		functional: { title: 'Functional', desc: 'Optional features and preference storage beyond what is strictly necessary.' },
		analytics: { title: 'Analytics', desc: 'Measurement of website use, subject to the required consent.' },
		performance: { title: 'Performance', desc: 'Performance measurement or optimisation tools, distinct from analytics.' },
		advertising: { title: 'Advertising and tracking', desc: 'Advertising-related storage and tracking, only if such technologies are deployed.' },
		unclassified: { title: 'Unclassified', desc: 'Technologies still under review, awaiting classification.' }
	},
	legal: {
		updated: 'Last updated: {date}',
		toc: 'On this page',
		manageCookies: 'Manage my cookie preferences',
		draftNotice: 'This document is a draft to be reviewed by group and our jurist legal counsel before deployment.'
	},
	auth: {
		brand: {
			title: 'One dashboard for all your identity verifications',
			points: {
				one: 'KYC cases, human review and full traceability',
				two: 'Switchable modules: liveness, biometrics, AML',
				three: 'Strict data isolation per organization'
			}
		},
		login: {
			title: 'Sign in',
			subtitle: 'Access your IZI LENS workspace.',
			email: 'Email address',
			password: 'Password',
			submit: 'Sign in',
			noAccount: 'No account yet?',
			signUp: 'Create an account',
			or: 'or',
			google: 'Continue with Google',
			registered: 'Account created. You can now sign in.',
			loggedOut: 'You have been signed out.',
			sessionExpired: 'Your session has expired. Please sign in again.'
		},
		register: {
			title: 'Create an account',
			subtitle: 'Get started in under two minutes.',
			fullName: 'Full name',
			email: 'Email address',
			password: 'Password',
			passwordHint: 'At least 12 characters.',
			confirm: 'Confirm password',
			submit: 'Create my account',
			haveAccount: 'Already have an account?',
			signIn: 'Sign in',
			terms: 'By continuing, you agree to our terms of use and privacy policy.'
		},
		errors: {
			invalid: 'Incorrect email or password.',
			generic: 'Something went wrong. Please try again in a moment.',
			required: 'This field is required.',
			email: 'Enter a valid email address.',
			passwordShort: 'Password must be at least 12 characters long.',
			passwordMismatch: 'Passwords do not match.',
			locked: 'Account temporarily locked after too many attempts.',
			unreachable: 'The service is temporarily unreachable.',
			oauth_failed: 'Sign-in with Google failed. Please try again.',
			oauth_unavailable: 'Sign-in with Google is not configured.',
			oauth_denied: 'No authorized account for this Google address.'
		}
	},
	app: {
		groups: { main: 'Main', modules: 'Modules', workspace: 'Workspace', admin: 'Kafintech administration' },
		nav: {
			overview: 'Overview',
			verifications: 'Verifications',
			newVerification: 'New verification',
			liveness: 'Liveness',
			biometrics: 'Biometrics',
			aml: 'AML screening',
			analytics: 'Analytics',
			apiKeys: 'API keys',
			team: 'Team',
			audit: 'Audit log',
			settings: 'Settings',
			developers: 'Developers',
			admin: 'Administration',
			adminOverview: 'Summary',
			tenants: 'Organizations',
			members: 'Members',
			announcements: 'Announcements',
			system: 'System'
		},
		signOut: 'Sign out',
		account: 'My account',
		soonBadge: 'Soon',
		openMenu: 'Open menu',
		backend: { ok: 'Service operational', down: 'Service unreachable' }
	},
	dashboard: {
		welcome: 'Hello, {name}',
		subtitle: "Here is your organization's verification activity.",
		stats: {
			total: 'Cases',
			pending: 'Pending review',
			approved: 'Approved',
			rejected: 'Rejected',
			confidence: 'Average OCR confidence',
			highRisk: 'High risk',
			approvalRate: 'Approval rate'
		},
		volume: 'Cases over 14 days',
		byStatus: 'Breakdown by status',
		byRisk: 'Breakdown by risk',
		recent: 'Latest cases',
		viewAll: 'View all',
		modules: 'Modules',
		quickActions: 'Quick actions',
		empty: { title: 'No cases yet', desc: 'Submit a first document to see your statistics appear.' }
	},
	verifications: {
		title: 'Verifications',
		subtitle: 'All KYC cases submitted by your organization.',
		new: 'New verification',
		searchPlaceholder: 'Reference or ID…',
		allStatuses: 'All statuses',
		allRisks: 'All risk levels',
		columns: { reference: 'Reference', type: 'Document', status: 'Status', risk: 'Risk', confidence: 'OCR confidence', date: 'Submitted' },
		empty: { title: 'No cases found', desc: 'Change your filters or submit a new verification.' },
		upload: {
			title: 'Submit a document',
			subtitle: 'The document is analyzed automatically; uncertain cases go to human review.',
			docType: 'Document type',
			reference: 'Your internal reference',
			referenceHint: 'Optional. Helps you find the case in your own system.',
			front: 'Front of the document',
			back: 'Back of the document',
			backHint: 'Optional. Stored for review, not read by OCR.',
			dropHint: 'Drop an image here or click to choose',
			sizeHint: 'JPEG, PNG or WebP · 8 MB maximum',
			submit: 'Start verification',
			success: 'Case created. Analysis in progress.',
			fileRequired: 'The front of the document is required.'
		},
		detail: {
			extracted: 'Extracted data',
			noExtracted: 'No data could be extracted.',
			flags: 'Risk signals',
			noFlags: 'No risk signal detected.',
			documents: 'Documents',
			ocr: 'OCR confidence',
			risk: 'Risk level',
			created: 'Submitted',
			processed: 'Analyzed',
			decided: 'Decided',
			failure: 'Failure reason',
			decisionTitle: 'Review decision',
			decisionHint: 'The decision is final and recorded in the audit log.',
			approve: 'Approve',
			reject: 'Reject',
			reason: 'Decision reason',
			reasonPlaceholder: 'Briefly explain your decision…',
			reasonRequired: 'A reason is required to reject a case.',
			decisionDone: 'Decision recorded.',
			alreadyDecided: 'A decision has already been made on this case.',
			notPending: 'This case is not awaiting review.',
			triggerLiveness: 'Request a liveness check',
			front: 'Front',
			back: 'Back',
			sharpness: 'Sharpness',
			fields: {
				surname: 'Surname',
				given_names: 'Given names',
				full_name: 'Full name',
				birth_date: 'Date of birth',
				birth_place: 'Place of birth',
				sex: 'Sex',
				height: 'Height',
				profession: 'Occupation',
				document_number: 'Document no.',
				id_number: 'Document no.',
				issue_date: 'Issued on',
				expiry_date: 'Expiry date',
				father: 'Father',
				mother: 'Mother',
				nationality: 'Nationality'
			}
		}
	},
	liveness: {
		title: 'Liveness',
		subtitle: 'When a case crosses a risk threshold, ask the person to film themselves from their phone.',
		howTitle: 'How it works',
		steps: {
			one: 'The risk threshold is reached, or you start the request manually.',
			two: 'A secure link (or a QR code) is sent to the person’s phone.',
			three: 'They follow the guided flow: face, movement, light.',
			four: 'The result comes back to the case and feeds the decision.'
		},
		generate: {
			title: 'Generate a verification link',
			caseRef: 'Case reference (optional)',
			button: 'Generate link',
			linkLabel: 'Link to send',
			scan: 'Scan this QR code with a phone',
			expires: 'Valid for {minutes} minutes',
			demo: 'Demo mode: the backend liveness module is not connected yet.',
			error: 'Could not create the session.'
		},
		threshold: {
			title: 'Automatic trigger',
			desc: 'Request liveness automatically from this risk level.',
			off: 'Off',
			medium: 'Medium risk and above',
			high: 'High risk only',
			saved: 'Threshold saved.'
		},
		mobile: {
			title: 'Liveness check',
			intro: 'Place your face in the frame, somewhere well lit. It takes less than 30 seconds.',
			start: 'Start',
			permission: 'Allow camera access to continue.',
			prompts: {
				center: 'Look straight ahead',
				left: 'Slowly turn your head left',
				right: 'Slowly turn your head right',
				blink: 'Blink your eyes'
			},
			capture: 'Capture',
			done: 'Thank you, check submitted.',
			doneText: 'You can close this page and go back to what you were doing.',
			invalid: 'This link is invalid or has expired.'
		}
	},
	modules: {
		status: { live: 'Active', soon: 'Soon', disabled: 'Not enabled' },
		kyc: { title: 'Document verification', desc: 'OCR, quality checks, risk signals and human review.' },
		liveness: { title: 'Liveness detection', desc: 'Prove the person is really present, live.' },
		biometrics: { title: 'Facial biometrics', desc: 'Compare the face with the document portrait.' },
		aml: { title: 'AML screening', desc: 'Sanctions, PEP and adverse media.' },
		api: { title: 'API & keys', desc: 'Embed verification in your products.' },
		soon: {
			badge: 'Module in preparation',
			desc: 'This module is planned in the dashboard and will be connected to the backend as soon as it ships.',
			planned: 'Planned'
		},
		biometrics_page: {
			title: 'Facial biometrics',
			subtitle: 'Face-to-document comparison and similarity score.',
			features: {
				match: 'Selfie comparison with the document portrait',
				score: 'Similarity score with configurable thresholds',
				quality: 'Face quality control',
				link: 'Result attached to the KYC case'
			}
		},
		aml_page: {
			title: 'AML screening',
			subtitle: 'Sanctions, politically exposed persons and adverse media.',
			features: {
				sanctions: 'International sanctions lists',
				pep: 'Politically exposed persons (PEP)',
				media: 'Adverse media search',
				rules: 'Risk rules configurable per organization'
			}
		},
		announcements_page: {
			title: 'Announcements',
			subtitle: 'Messages broadcast to customer organizations.',
			features: {
				banner: 'Information banner in the dashboard',
				target: 'Targeting by organization or module',
				schedule: 'Scheduling and expiry'
			}
		}
	},
	analytics: {
		title: 'Analytics',
		subtitle: 'Trends computed over the latest 200 cases.',
		confidence: 'OCR confidence distribution',
		daily: 'Daily volume',
		bands: { low: 'Under 70%', mid: '70 – 90%', high: 'Over 90%' }
	},
	apiKeys: {
		title: 'API keys',
		subtitle: 'Programmatic access to your verifications. Each key is tied to your organization.',
		create: 'Create a key',
		name: 'Key name',
		namePlaceholder: 'E.g. Mobile app — production',
		expiry: 'Expiry',
		expiryNever: 'Never',
		expiry30: '30 days',
		expiry90: '90 days',
		expiry365: '1 year',
		columns: { name: 'Name', prefix: 'Prefix', created: 'Created', lastUsed: 'Last used', expires: 'Expires', status: 'Status' },
		revoke: 'Revoke',
		revokeConfirm: 'Revoke the key “{name}”? Applications using it will stop working.',
		revoked: 'Revoked',
		expired: 'Expired',
		created: 'Key created',
		showOnce: 'Copy this key now: it will never be shown again.',
		empty: { title: 'No API keys', desc: 'Create a key to call the API from your applications.' }
	},
	team: {
		title: 'Team',
		subtitle: 'The members of your organization and their roles.',
		invite: 'Add a member',
		fullName: 'Full name',
		tempPassword: 'Temporary password',
		tempPasswordHint: 'At least 12 characters. Share it with the member.',
		columns: { member: 'Member', role: 'Role', status: 'Status', lastLogin: 'Last sign-in' },
		deactivate: 'Deactivate',
		activate: 'Reactivate',
		added: 'Member added.',
		updated: 'Member updated.',
		roleHelp: {
			admin: 'Manages keys, team and settings.',
			reviewer: 'Reviews cases and makes decisions.',
			viewer: 'Views cases in read-only mode.',
			integration: 'Technical account for integrations.'
		}
	},
	audit: {
		title: 'Audit log',
		subtitle: 'Append-only history of all sensitive actions.',
		columns: { date: 'Date', actor: 'Actor', action: 'Action', resource: 'Resource', ip: 'IP address' },
		empty: { title: 'No audit entries', desc: 'Actions will show up here as soon as they happen.' },
		actors: { user: 'User', api_key: 'API key', system: 'System' }
	},
	settings: {
		title: 'Settings',
		subtitle: 'Your profile, preferences and account security.',
		profile: { title: 'Profile', fullName: 'Full name', email: 'Email', saved: 'Profile updated.' },
		preferences: { title: 'Preferences', language: 'Interface language', theme: 'Theme' },
		organization: { title: 'Organization', slug: 'Identifier', modules: 'Enabled modules', readonly: 'Contact Kafintech to change your organization’s modules.' },
		security: {
			title: 'Security',
			currentPassword: 'Current password',
			newPassword: 'New password',
			change: 'Change password',
			changed: 'Password updated.',
			googleNote: 'Signed in with Google? Your password is managed by Google.'
		}
	},
	developers: {
		title: 'Developers',
		subtitle: 'Call the IZI LENS API from your applications in three steps.',
		step1: 'Create an API key',
		step1Text: 'From the API keys page. It is only shown once.',
		step2: 'Submit a document',
		step3: 'Read the result',
		docs: 'Full API documentation',
		baseUrl: 'Base URL',
		health: 'Service status'
	},
	admin: {
		title: 'Kafintech administration',
		subtitle: 'Area reserved for platform super administrators.',
		stats: { tenants: 'Organizations', members: 'Members', activeTenants: 'Active organizations' },
		recentActivity: 'Recent activity',
		tenants: {
			title: 'Organizations',
			subtitle: 'Platform customers and the modules open to them.',
			create: 'New organization',
			slug: 'Identifier (slug)',
			slugHint: 'Lowercase letters, digits and hyphens.',
			adminEmail: 'First administrator email',
			modules: 'Modules',
			columns: { name: 'Organization', slug: 'Identifier', modules: 'Modules', status: 'Status', created: 'Created' },
			created: 'Organization created.',
			updated: 'Organization updated.',
			suspend: 'Suspend',
			reactivate: 'Reactivate',
			detail: 'Organization detail',
			members: 'Organization members',
			noMembers: 'No members.'
		},
		members: { title: 'Members', subtitle: 'All platform users.', org: 'Organization' },
		system: {
			title: 'System',
			subtitle: 'Backend status and environment configuration.',
			backend: 'Backend service',
			baseUrl: 'Service URL',
			oidc: 'Google sign-in (OIDC)',
			configured: 'Configured',
			missing: 'Not configured',
			loginFormat: 'Login format'
		}
	},
	status: {
		processing: 'Processing',
		pending_review: 'Pending review',
		approved: 'Approved',
		rejected: 'Rejected',
		failed: 'Failed'
	},
	risk: { low: 'Low', medium: 'Medium', high: 'High', none: 'Not assessed' },
	roles: {
		super_admin: 'Super administrator',
		admin: 'Administrator',
		reviewer: 'Reviewer',
		viewer: 'Viewer',
		integration: 'Integration'
	},
	docTypes: { cni_cm: 'National ID card (Cameroon)' },
	errors: {
		forbidden: "You don't have access to this page.",
		notFound: 'This page could not be found.',
		backend_unreachable: 'The backend service is unreachable. Check BACKEND_SERVICE_URL.',
		generic: 'Something went wrong.',
		goHome: 'Back to home',
		goDashboard: 'Back to dashboard'
	},
	toast: { saved: 'Changes saved.', error: 'The action failed.', copied: 'Copied to clipboard.' }
};

export default en;
