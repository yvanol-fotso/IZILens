export const DEFAULT_PRICING_GRID = {
	plans: {
		starter: { 
			monthly: { CAD: 99, USD: 79, EUR: 69, XOF: 49000, XAF: 49000 }, 
			annual: { CAD: 990, USD: 790, EUR: 690, XOF: 490000, XAF: 490000 },
			minimum_commitment: { CAD: 0, USD: 0, EUR: 0, XOF: 0, XAF: 0 }
		},
		business: { 
			monthly: { CAD: 299, USD: 239, EUR: 209, XOF: 149000, XAF: 149000 }, 
			annual: { CAD: 2990, USD: 2390, EUR: 2090, XOF: 1490000, XAF: 1490000 },
			minimum_commitment: { CAD: 0, USD: 0, EUR: 0, XOF: 0, XAF: 0 }
		},
		enterprise: { 
			monthly: { CAD: 999, USD: 799, EUR: 699, XOF: 499000, XAF: 499000 }, 
			annual: { CAD: 9990, USD: 7990, EUR: 6990, XOF: 4990000, XAF: 4990000 },
			minimum_commitment: { CAD: 1500, USD: 1200, EUR: 1100, XOF: 750000, XAF: 750000 }
		}
	},
	usage: {
		kyc: { CAD: 1.50, USD: 1.20, EUR: 1.10, XOF: 750, XAF: 750 },
		kyb: { CAD: 4.50, USD: 3.60, EUR: 3.30, XOF: 2250, XAF: 2250 },
		biometrics: { CAD: 0.80, USD: 0.65, EUR: 0.60, XOF: 400, XAF: 400 }
	},
	options: { 
		monitoring_monthly: { CAD: 49, USD: 39, EUR: 35, XOF: 24000, XAF: 24000 } 
	},
	integration_fee: { 
		enabled: true, 
		amounts: { CAD: 2500, USD: 2000, EUR: 1800, XOF: 1200000, XAF: 1200000 } 
	}
};

export type PriceGrid = typeof DEFAULT_PRICING_GRID;
export type Plan = 'starter' | 'business' | 'enterprise';
export type Service = 'kyc' | 'kyb' | 'biometrics';