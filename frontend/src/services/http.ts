/** Shared safe transport; never expose raw response bodies or native errors. */
const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";
const REQUEST_TIMEOUT_MS = 30_000;

export class ApiClientError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
  ) {
    super(message);
  }
}

interface SafeMessages {
  unavailable: string;
  invalidResponse: string;
  statuses?: Partial<Record<number, string>>;
}

async function safeResponse(
  path: string,
  options: RequestInit,
  messages: SafeMessages,
): Promise<Response> {
  let response: Response;
  try {
    response = await fetch(`${baseUrl}${path}`, {
      ...options,
      credentials: "same-origin",
      cache: "no-store",
      signal: options.signal
        ? AbortSignal.any([options.signal, AbortSignal.timeout(REQUEST_TIMEOUT_MS)])
        : AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });
  } catch {
    throw new ApiClientError(messages.unavailable);
  }
  if (!response.ok) {
    throw new ApiClientError(
      messages.statuses?.[response.status] ?? messages.unavailable,
      response.status,
    );
  }
  return response;
}

export async function requestJson<T>(
  path: string,
  options: RequestInit,
  parse: (value: unknown) => T,
  messages: SafeMessages,
): Promise<T> {
  const response = await safeResponse(path, options, messages);
  try {
    return parse(await response.json());
  } catch {
    throw new ApiClientError(messages.invalidResponse);
  }
}

export async function requestNoContent(
  path: string,
  options: RequestInit,
  messages: SafeMessages,
): Promise<void> {
  const response = await safeResponse(path, options, messages);
  if (response.status !== 204) throw new ApiClientError(messages.invalidResponse);
}
