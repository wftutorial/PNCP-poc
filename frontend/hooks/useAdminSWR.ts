import useSWR, { type SWRConfiguration } from "swr";
import { useAuth } from "../app/components/AuthProvider";

function createAdminFetcher(token: string) {
  return async (url: string) => {
    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.status === 403) throw new Error("Acesso negado. Você não é administrador.");
    if (!res.ok) throw new Error(`Erro ${res.status}`);
    return res.json();
  };
}

export function useAdminSWR<T = unknown>(key: string | null, config?: SWRConfiguration) {
  const { session } = useAuth();
  const token = session?.access_token;

  return useSWR<T>(
    token && key ? key : null,
    token ? createAdminFetcher(token) : null,
    {
      revalidateOnFocus: false,
      ...config,
    },
  );
}

const publicFetcher = async (url: string) => {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Erro ${res.status}`);
  return res.json();
};

export function usePublicSWR<T = unknown>(key: string | null, config?: SWRConfiguration) {
  return useSWR<T>(key, publicFetcher, {
    revalidateOnFocus: false,
    ...config,
  });
}
