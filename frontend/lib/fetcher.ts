/**
 * TD-008 AC2: SWR fetcher with auth headers and error handling.
 */
export class FetchError extends Error {
  status: number;
  info: unknown;
  constructor(message: string, status: number, info?: unknown) {
    super(message);
    this.name = "FetchError";
    this.status = status;
    this.info = info;
  }
}

export const fetcher = async (url: string) => {
  const res = await fetch(url);
  if (!res.ok) {
    let info: unknown;
    try {
      info = await res.json();
    } catch {
      info = await res.text().catch(() => null);
    }
    throw new FetchError(
      `HTTP ${res.status}: ${res.statusText}`,
      res.status,
      info
    );
  }
  return res.json();
};
