import { createBrowserClient } from "@supabase/ssr";
import type { SupabaseClient } from "@supabase/supabase-js";

let _client: SupabaseClient | null = null;
let _missingEnvWarned = false;

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

export function isSupabaseConfigured(): boolean {
  return Boolean(supabaseUrl && supabaseAnonKey);
}

export function getSupabase(): SupabaseClient | null {
  if (!_client) {
    if (!isSupabaseConfigured()) {
      if (!_missingEnvWarned && process.env.NODE_ENV !== "production") {
        _missingEnvWarned = true;
        console.warn(
          "[Supabase] NEXT_PUBLIC_SUPABASE_URL ou NEXT_PUBLIC_SUPABASE_ANON_KEY não configurados. Recursos de autenticação serão desativados até configurar o .env.local."
        );
      }
      return null;
    }

    _client = createBrowserClient(supabaseUrl!, supabaseAnonKey!, {
      auth: { flowType: "pkce" },
    });
  }
  return _client;
}

function getSupabaseOrThrow(): SupabaseClient {
  const client = getSupabase();
  if (!client) {
    throw new Error(
      "Supabase não configurado. Defina NEXT_PUBLIC_SUPABASE_URL e NEXT_PUBLIC_SUPABASE_ANON_KEY no frontend/.env.local."
    );
  }
  return client;
}

// Backward-compatible export — lazy via Proxy so no createBrowserClient() at import time
export const supabase = new Proxy({} as SupabaseClient, {
  get(_target, prop, receiver) {
    return Reflect.get(getSupabaseOrThrow(), prop, receiver);
  },
});
