export type Ticket = { id: number; customer_email: string; subject: string; message: string; status: string };
export type Knowledge = { id: number; title: string; content: string };
export type AIResult = { category: string; priority: string; suggested_response: string };
export type RAGResult = { answer: string; sources: string[]; grounded: boolean };
export type User = { id: number; email: string };
export class APIError extends Error { constructor(public status: number, message: string) { super(message); } }

async function request<T>(path: string, token: string | null, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (token) headers.set('Authorization', `Bearer ${token}`);
  if (options.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  let response: Response;
  try { response = await fetch(`/api${path}`, { ...options, headers }); }
  catch { throw new APIError(0, 'Cannot reach backend. Check that Docker is running on port 8000.'); }
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = body?.detail;
    const reason = typeof detail === 'string' ? detail : Array.isArray(detail) ? detail.map((item: { msg?: string }) => item.msg).join(', ') : `Request failed (${response.status})`;
    throw new APIError(response.status, reason);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  register: (email: string, password: string) => request<User>('/auth/register', null, { method: 'POST', body: JSON.stringify({ email, password }) }),
  login: async (email: string, password: string) => {
    const form = new URLSearchParams({ username: email, password });
    return request<{ access_token: string }>('/auth/token', null, { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: form.toString() });
  },
  me: (token: string) => request<User>('/auth/me', token),
  tickets: (token: string) => request<Ticket[]>('/tickets', token),
  createTicket: (token: string, input: Omit<Ticket, 'id' | 'status'>) => request<Ticket>('/tickets', token, { method: 'POST', body: JSON.stringify(input) }),
  changeStatus: (token: string, id: number, status: string) => request<Ticket>(`/tickets/${id}/status`, token, { method: 'PATCH', body: JSON.stringify({ status }) }),
  aiAnalyze: (token: string, id: number) => request<AIResult>(`/tickets/${id}/ai-analyze`, token, { method: 'POST' }),
  ragAnalyze: (token: string, id: number) => request<RAGResult>(`/tickets/${id}/rag-analyze`, token, { method: 'POST' }),
  knowledge: (token: string) => request<Knowledge[]>('/knowledge', token),
  addKnowledge: (token: string, input: Pick<Knowledge, 'title' | 'content'>) => request<Knowledge>('/knowledge', token, { method: 'POST', body: JSON.stringify(input) }),
  deleteKnowledge: (token: string, id: number) => request<void>(`/knowledge/${id}`, token, { method: 'DELETE' }),
};
