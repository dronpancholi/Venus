export interface EngineeringEvent {
  id: string;
  type: string;
  origin: string;
  payload: Record<string, unknown>;
  timestamp: number;
  tags: string[];
}

export interface HealthStatus {
  status: string;
  uptime_seconds: number;
  services: number;
  messages: number;
  sessions: number;
}

export interface ServiceInstance {
  id?: string;
  instance_id?: string;
  name?: string;
  type?: string;
  status?: string;
}

export interface TaskSummary {
  total?: number;
  pending?: number;
  running?: number;
  completed?: number;
  failed?: number;
  tasks?: TaskItem[];
}

export interface TaskItem {
  id: string;
  name: string;
  status: string;
  priority?: string;
  assigned_to?: string;
  created_at?: string;
}

export interface AgentSummary {
  agents?: AgentItem[];
}

export interface AgentItem {
  id: string;
  name: string;
  status: string;
  capabilities?: string[];
}

export interface SearchResult {
  type: string;
  label: string;
  relevance: number;
  id?: string;
}

export interface SearchResponse {
  results: SearchResult[];
  count: number;
}

export interface Conversation {
  id: string;
  title: string;
  created_at?: string;
  updated_at?: string;
  message_count?: number;
}

export interface MetricSnapshot {
  metrics?: Record<string, number>;
  histogram_details?: Record<string, number[]>;
}

export interface AuditEntry {
  id: string;
  action: string;
  actor: string;
  resource: string;
  detail: string;
  timestamp: number;
  severity: string;
}

export interface ProjectInfo {
  name: string;
  path: string;
  imported_at: string;
  total_files: number;
  total_size_bytes: number;
}

export interface WatcherState {
  active: boolean;
  last_scan: string;
  scan_count: number;
  change_count: number;
  error_count: number;
}

export interface RepositoryStatus {
  active: boolean;
  watchers?: Record<string, WatcherState>;
}

export interface ProviderInfo {
  id: string;
  healthy: boolean;
  model?: string;
}

export interface StorageStats {
  connected: boolean;
  table_sizes?: Record<string, number>;
}

export interface KernelStats {
  uptime: number;
  services: number;
  messages: number;
  events: number;
}
