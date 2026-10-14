import { apiCall } from './apiClient';

export interface CheckoutResponse {
  url: string;
  session_id: string;
}

export async function createCheckoutSession(priceId: string): Promise<CheckoutResponse> {
  return apiCall<CheckoutResponse>('/api/v1/payments/create-checkout-session', 'POST', {
    price_id: priceId,
  });
}

export async function fetchPackages(): Promise<{
  packages: Array<{
    id: string;
    price_id: string;
    name: string;
    tokens: number;
    bonus_tokens: number;
    price_usd: number;
  }>;
}> {
  return apiCall('/api/v1/payments/packages', 'GET');
}
