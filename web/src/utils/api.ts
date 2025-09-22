import { createClient } from '@supabase/supabase-js';

// Web-specific API utilities using web project dependencies
const getSupabaseClient = () => {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
  
  if (!supabaseUrl || !supabaseAnonKey) {
    console.warn('Missing Supabase environment variables');
    return null;
  }

  return createClient(supabaseUrl, supabaseAnonKey);
};

// Get authentication headers for API calls
export async function getAuthHeaders(): Promise<Record<string, string>> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  try {
    const supabase = getSupabaseClient();
    if (supabase) {
      const { data: { session } } = await supabase.auth.getSession();
      
      if (session?.access_token) {
        headers['Authorization'] = `Bearer ${session.access_token}`;
      }
    }
  } catch (error) {
    console.warn('Failed to get auth session:', error);
  }

  return headers;
}

// Helper for making authenticated API requests
export async function authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const authHeaders = await getAuthHeaders();
  
  return fetch(url, {
    ...options,
    headers: {
      ...authHeaders,
      ...options.headers,
    },
  });
}