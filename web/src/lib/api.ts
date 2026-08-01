import type {
  HealthStatus,
  ServiceInstance,
  TaskSummary,
  AgentSummary,
  SearchResponse,
  Conversation,
  MetricSnapshot,
  AuditEntry,
  ProjectInfo,
  RepositoryStatus,
  ProviderInfo,
  StorageStats,
  KernelStats,
} from './types';

const BASE = '/v1';

async function fetchAPI<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status}: ${text.slice(0, 200)}`);
  }
  return res.json();
}

export const api = {
  health: () => fetchAPI<HealthStatus>('/health'),

  kernelStats: () => fetchAPI<KernelStats>('/kernel/stats'),

  events: (params?: { event_type?: string; origin?: string; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.event_type) q.set('event_type', params.event_type);
    if (params?.origin) q.set('origin', params.origin);
    if (params?.limit) q.set('limit', String(params.limit));
    return fetchAPI<{ events: unknown[]; count: number }>(`/events?${q}`);
  },

  services: () => fetchAPI<{ count: number; services: ServiceInstance[] }>('/services'),

  service: (id: string) => fetchAPI<ServiceInstance>(`/services/${id}`),

  agents: () => fetchAPI<AgentSummary>('/agents'),

  tasks: (status?: string) => {
    const q = status ? `?status=${status}` : '';
    return fetchAPI<TaskSummary>(`/tasks${q}`);
  },

  conversations: (query?: string) => {
    const q = query ? `?query=${encodeURIComponent(query)}` : '';
    return fetchAPI<{ conversations: Conversation[] }>(`/conversations${q}`);
  },

  conversationMessages: (id: string) =>
    fetchAPI<{ messages: unknown[]; count: number }>(`/conversations/${id}/messages`),

  metrics: () => fetchAPI<MetricSnapshot>('/metrics'),

  audit: (params?: { action?: string; actor?: string; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.action) q.set('action', params.action);
    if (params?.actor) q.set('actor', params.actor);
    if (params?.limit) q.set('limit', String(params.limit));
    return fetchAPI<{ entries: AuditEntry[]; count: number; total: number }>(`/audit?${q}`);
  },

  search: (query: string, sources = 'all') =>
    fetchAPI<SearchResponse>(`/search?query=${encodeURIComponent(query)}&sources=${sources}&limit=20`),

  providers: () => fetchAPI<{ providers: ProviderInfo[] }>('/providers'),

  storage: () => fetchAPI<StorageStats>('/storage'),

  repository: () => fetchAPI<RepositoryStatus>('/repository'),

  execution: () => fetchAPI<{ execution_count: number }>('/execution'),

  authStatus: () => fetchAPI<{ auth: boolean; message: string }>('/auth/status'),

  emitEvent: (event_type: string, payload: Record<string, unknown> = {}, origin = 'web') =>
    fetchAPI<{ id: string; type: string; timestamp: number }>('/events/emit', {
      method: 'POST',
      body: JSON.stringify({ event_type, payload, origin }),
    }),
};
