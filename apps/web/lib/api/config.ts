/** Browser talks only to TradePulse API — never to LLM/GLEIF/sanctions directly. */

export function apiBaseUrl(): string {
  return (
    process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ||
    "http://127.0.0.1:8000/api/v1"
  );
}
