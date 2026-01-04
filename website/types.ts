
export interface Feature {
  title: string;
  description: string;
  icon: React.ReactNode;
}

export interface PricingPlan {
  name: string;
  price: string;
  period: string;
  features: string[];
  recommended?: boolean;
}

export type AuthMode = 'login' | 'register';
